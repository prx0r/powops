"""Cross-garden health aggregation engine.

Loads sources.yaml, reads health artifacts from each garden,
and produces a unified list of SourceStatus objects.
"""

import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .garden import (
    GardenReader,
    SourceStatus,
    _compute_check_hash,
)


SOURCES_YAML = Path(__file__).parent / "sources.yaml"


def load_manifest(path: Optional[Path] = None) -> dict:
    """Load the sources.yaml manifest."""
    path = path or SOURCES_YAML
    with open(path) as f:
        return yaml.safe_load(f)


def check_source(source: dict, readers: dict, gardens: dict | None = None) -> SourceStatus:
    """Check a single source against its garden reader."""
    garden_id = source.get("garden", "")
    health = source.get("health", {})
    check_type = health.get("check", "unknown")
    now = datetime.now(timezone.utc)
    gardens = gardens or {}

    reader = readers.get(garden_id)

    # Garden not installed
    garden_cfg = gardens.get(garden_id, {})
    if garden_cfg.get("status") == "not_installed":
        return SourceStatus(
            source_id=source["id"],
            garden=garden_id,
            authority=source.get("authority", ""),
            description=source.get("description", ""),
            status="not_installed",
            checked_at=now,
        )

    # Source explicitly marked not installed
    if source.get("status") == "not_installed":
        return SourceStatus(
            source_id=source["id"],
            garden=garden_id,
            authority=source.get("authority", ""),
            description=source.get("description", ""),
            status="not_installed",
            checked_at=now,
        )

    # API key required but not set
    api_key_env = source.get("api_key_env")
    if api_key_env:
        import os
        if not os.environ.get(api_key_env):
            return SourceStatus(
                source_id=source["id"],
                garden=garden_id,
                authority=source.get("authority", ""),
                description=source.get("description", ""),
                status="no_key",
                error=f"Missing {api_key_env}",
                checked_at=now,
            )

    if reader is None or not reader.exists():
        return SourceStatus(
            source_id=source["id"],
            garden=garden_id,
            authority=source.get("authority", ""),
            description=source.get("description", ""),
            status="unknown",
            error=f"Garden not found at {garden_cfg.get('path', '?')}",
            checked_at=now,
        )

    # Dispatch to the right reader method
    if check_type == "heartbeat":
        status = reader.read_heartbeat(health)
    elif check_type == "collector_db":
        status = reader.read_collector_db(health)
    elif check_type == "raw_mtime":
        status = reader.read_raw_mtime(health)
    elif check_type == "pid_file":
        status = reader.read_pid_file(health)
    elif check_type == "pow_health":
        status = reader.read_pow_health(health.get("source_id", source["id"]), health)
    else:
        return SourceStatus(
            source_id=source["id"],
            garden=garden_id,
            authority=source.get("authority", ""),
            description=source.get("description", ""),
            status="unknown",
            error=f"Unknown check type: {check_type}",
        )

    # Fill in source metadata
    status.source_id = source["id"]
    status.authority = source.get("authority", "")
    status.description = source.get("description", "")
    status.checked_at = datetime.now(timezone.utc)
    status.check_hash = _compute_check_hash(
        source["id"], status.status, status.checked_at.isoformat()
    )
    return status


def check_all(path: Optional[Path] = None) -> List[SourceStatus]:
    """Check all sources across all gardens."""
    manifest = load_manifest(path)
    gardens = manifest.get("gardens", {})
    sources = manifest.get("sources", [])

    # Build readers
    readers = {}
    for gid, gcfg in gardens.items():
        if gcfg.get("status") != "not_installed":
            readers[gid] = GardenReader(gid, gcfg)

    # NOTE: no event recording here. check_all is a read path used by the
    # dashboard, MCP and CLI — it must not write. Events are recorded in
    # check_all_full, which owns the alert-state lifecycle. Recording here
    # caused duplicate transition events on every read (state never advances
    # on this path).

    results = []
    for source in sources:
        results.append(check_source(source, readers, gardens))

    return results


def check_all_full(
    path: Optional[Path] = None,
    record_history: bool = True,
    record_volume: bool = True,
    fire_alerts: bool = True,
    dry_run: bool = False,
) -> dict:
    """Run a full check cycle: check + history + volume + alerts.

    This is the main entry point for periodic monitoring.
    Returns a summary dict with results and actions taken.
    """
    results = check_all(path)

    actions = {
        "history_recorded": False,
        "volume_recorded": False,
        "alerts_fired": [],
    }

    if record_history:
        from .history import record_check
        record_check(results)
        actions["history_recorded"] = True

    if record_volume:
        from .volume import record_volume as _record_volume
        _record_volume(results)
        actions["volume_recorded"] = True

    if fire_alerts:
        from .alerts import process_alerts
        from .alerts import _load_alert_state
        # Snapshot pre-run state BEFORE process_alerts saves new state.
        # The incident comparison below must use this, not the updated file.
        pre_state = _load_alert_state()
        manifest = load_manifest(path)
        sources = manifest.get("sources", [])

        # Build alert configs from sources.yaml
        alert_configs = {}
        for s in sources:
            sid = s.get("id", "")
            alert_cfg = s.get("alert", {})
            if alert_cfg:
                alert_configs[sid] = alert_cfg

        alert_actions = process_alerts(results, alert_configs, dry_run=dry_run)
        actions["alerts_fired"] = alert_actions

        # Record events for status changes (live runs only — dry runs
        # must not write to the event stream).
        from .events import record_event
        if not dry_run:
            for a in alert_actions:
                sid = a.get("source_id", "")
                action = a.get("action", "")
                new_status = a.get("new_status", "")
                # Find the matching result for garden info
                match = [r for r in results if r.source_id == sid]
                garden = match[0].garden if match else ""
                if action == "alert":
                    record_event(
                        event_type=f"source_{new_status}",
                        garden=garden,
                        source_id=sid,
                        severity="critical" if new_status == "error" else "warning",
                        details={"webhook": a.get("webhook", {})},
                    )
                elif action == "recovery":
                    record_event(
                        event_type="source_recovered",
                        garden=garden,
                        source_id=sid,
                        severity="info",
                    )

        # Process incidents on state transitions.
        # Idempotency guard: never open when one is already open for the
        # source (same-day IDs would otherwise overwrite + re-emit events
        # on every run). Unknown previous state means first sighting —
        # observe, don't open (matches alert semantics).
        from .incidents import (
            create_incident, update_incident, resolve_incident,
            find_open_incident,
        )
        for r in results:
            if not r.source_id:
                continue
            if dry_run:
                continue
            old_status = pre_state.get(r.source_id, {}).get("status", "unknown")
            new_status = r.status

            if old_status == new_status:
                continue

            # Problem emerged: open incident
            if old_status == "ok" and new_status in ("stale", "error", "blocked", "no_key"):
                if find_open_incident(r.source_id, r.garden):
                    continue
                severity = "critical" if new_status == "error" else "warning"
                incident = create_incident(
                    source_id=r.source_id,
                    garden=r.garden,
                    severity=severity,
                    reason=f"Status changed from ok to {new_status}",
                    last_success=r.last_success.isoformat() if r.last_success else None,
                    error=r.error,
                )
                record_event(
                    event_type="incident_opened",
                    garden=r.garden,
                    source_id=r.source_id,
                    incident_id=incident["incident_id"],
                    severity=severity,
                )

            # Problem deepened: update incident
            elif old_status in ("stale", "no_key") and new_status == "error":
                existing = find_open_incident(r.source_id, r.garden)
                if existing:
                    update_incident(
                        existing["incident_id"],
                        severity="critical",
                        reason=f"Status degraded from {old_status} to {new_status}",
                        error=r.error,
                    )
                    record_event(
                        event_type="incident_updated",
                        garden=r.garden,
                        source_id=r.source_id,
                        incident_id=existing["incident_id"],
                        severity="critical",
                    )

            # Recovered: resolve incident
            elif old_status in ("stale", "error", "blocked", "no_key") and new_status == "ok":
                existing = find_open_incident(r.source_id, r.garden)
                if existing:
                    resolve_incident(existing["incident_id"])
                    record_event(
                        event_type="incident_closed",
                        garden=r.garden,
                        source_id=r.source_id,
                        incident_id=existing["incident_id"],
                        severity="info",
                    )

    # Schema drift detection (runs after alerts/incidents)
    actions["schema_drifts"] = []
    for r in results:
        if r.source_id and r.details:
            schema_info = r.details.get("schema")
            if schema_info:
                from .schema import check_and_update_schema
                drift = check_and_update_schema(r.source_id, r.garden, schema_info)
                if drift:
                    actions["schema_drifts"].append(drift)
                    from .events import record_event
                    record_event(
                        event_type="schema_changed",
                        garden=r.garden,
                        source_id=r.source_id,
                        details={"drifts": drift.get("drifts", [])},
                    )

    # Volume anomaly detection
    actions["volume_anomalies"] = []
    for r in results:
        if r.source_id and r.records is not None:
            from .volume import detect_volume_anomaly
            anomaly = detect_volume_anomaly(r.source_id, r.records)
            if anomaly:
                actions["volume_anomalies"].append(anomaly)
                from .events import record_event
                record_event(
                    event_type="volume_anomaly",
                    garden=r.garden,
                    source_id=r.source_id,
                    severity="warning",
                    details=anomaly,
                )

    return {
        "results": results,
        "overall": overall_status(results),
        "gardens": garden_summary(results),
        "actions": actions,
    }


def garden_summary(results: List[SourceStatus]) -> dict:
    """Compute per-garden summary stats."""
    gardens = {}
    for r in results:
        if r.garden not in gardens:
            gardens[r.garden] = {
                "total": 0, "ok": 0, "stale": 0, "error": 0,
                "blocked": 0, "no_key": 0, "not_installed": 0, "unknown": 0,
            }
        g = gardens[r.garden]
        g["total"] += 1
        g[r.status] = g.get(r.status, 0) + 1
    return gardens


def overall_status(results: List[SourceStatus]) -> str:
    """Compute overall system status."""
    active = [r for r in results if r.status not in ("not_installed", "unknown")]
    if not active:
        return "no_data"
    if all(r.status == "ok" for r in active):
        return "all_ok"
    if any(r.status == "error" for r in active):
        return "degraded"
    if any(r.status == "stale" for r in active):
        return "partial_outage"
    return "ok"
