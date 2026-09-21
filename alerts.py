"""Alerting — webhook notifications on state transitions.

State machine per source:
  ok → alerting (fires webhook)
  alerting → ok (fires recovery webhook)
  alerting → alerting (suppressed, no duplicate alerts)

Alert state is persisted in a JSON file to survive restarts.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .garden import SourceStatus


ALERT_STATE_FILE = Path(__file__).parent / "alert_state.json"


def _load_alert_state() -> dict:
    """Load the current alert state for all sources."""
    if ALERT_STATE_FILE.exists():
        with open(ALERT_STATE_FILE) as f:
            return json.load(f)
    return {}


def _save_alert_state(state: dict) -> None:
    """Persist alert state."""
    ALERT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = ALERT_STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, ALERT_STATE_FILE)


def _fire_webhook(url: str, payload: dict, timeout: int = 10) -> dict:
    """POST JSON to a webhook URL. Returns {ok, status, error}."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _build_alert_payload(
    source_id: str,
    garden: str,
    old_status: str,
    new_status: str,
    status_obj: Optional[SourceStatus] = None,
) -> dict:
    """Build the webhook payload for an alert."""
    now = datetime.now(timezone.utc).isoformat()
    severity = "critical" if new_status == "error" else "warning"

    return {
        "event": "status_change",
        "source_id": source_id,
        "garden": garden,
        "old_status": old_status,
        "new_status": new_status,
        "severity": severity,
        "timestamp": now,
        "details": {
            "last_good": status_obj.last_good.isoformat() if status_obj and status_obj.last_good else None,
            "age_seconds": int(status_obj.age.total_seconds()) if status_obj and status_obj.age else None,
            "error": status_obj.error if status_obj else None,
            "records": status_obj.records if status_obj else None,
        },
    }


def _build_recovery_payload(
    source_id: str,
    garden: str,
    status_obj: Optional[SourceStatus] = None,
) -> dict:
    """Build the webhook payload for a recovery notification."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "event": "recovery",
        "source_id": source_id,
        "garden": garden,
        "old_status": "alerting",
        "new_status": "ok",
        "severity": "info",
        "timestamp": now,
        "details": {
            "last_good": status_obj.last_good.isoformat() if status_obj and status_obj.last_good else None,
            "age_seconds": int(status_obj.age.total_seconds()) if status_obj and status_obj.age else None,
            "records": status_obj.records if status_obj else None,
        },
    }


def _should_alert(source_id: str, new_status: str, alert_config: dict) -> bool:
    """Determine if an alert should fire based on config thresholds."""
    # Don't alert for not_installed or unknown (those are expected)
    if new_status in ("not_installed", "unknown"):
        return False

    # Don't alert if alerts are disabled for this source
    if not alert_config.get("enabled", True):
        return False

    # Check severity thresholds
    severity = alert_config.get("severity", {})
    if new_status == "stale":
        return severity.get("stale", True)
    elif new_status == "error":
        return severity.get("error", True)
    elif new_status == "no_key":
        return severity.get("no_key", False)

    return False


def process_alerts(
    results: List[SourceStatus],
    alert_configs: Optional[dict] = None,
    dry_run: bool = False,
) -> List[dict]:
    """Process check results and fire alerts on state transitions.

    Args:
        results: Current check results
        alert_configs: Per-source alert config from sources.yaml
        dry_run: If True, don't actually send webhooks

    Returns:
        List of alert actions taken
    """
    state = _load_alert_state()
    alert_configs = alert_configs or {}
    actions = []

    for r in results:
        source_id = r.source_id
        if not source_id:
            continue

        # Get alert config for this source
        source_alert = alert_configs.get(source_id, {})
        if not source_alert.get("enabled", True):
            continue

        old_status = state.get(source_id, {}).get("status", "unknown")
        new_status = r.status

        # State transition detection
        if old_status == new_status:
            continue

        # ok → problem: fire alert
        if old_status == "ok" and new_status in ("stale", "error", "blocked", "no_key"):
            if _should_alert(source_id, new_status, source_alert):
                webhook_url = source_alert.get("webhook_url") or source_alert.get("notify", {}).get("webhook")
                if webhook_url and not dry_run:
                    payload = _build_alert_payload(source_id, r.garden, old_status, new_status, r)
                    result = _fire_webhook(webhook_url, payload)
                    actions.append({
                        "source_id": source_id,
                        "action": "alert",
                        "new_status": new_status,
                        "webhook": result,
                    })
                else:
                    actions.append({
                        "source_id": source_id,
                        "action": "alert",
                        "new_status": new_status,
                        "webhook": {"ok": False, "error": "dry_run or no webhook"} if not dry_run else {"ok": True, "dry_run": True},
                    })

        # problem → ok: fire recovery
        elif old_status in ("stale", "error", "blocked", "no_key") and new_status == "ok":
            webhook_url = source_alert.get("webhook_url") or source_alert.get("notify", {}).get("webhook")
            if webhook_url and not dry_run:
                payload = _build_recovery_payload(source_id, r.garden, r)
                result = _fire_webhook(webhook_url, payload)
                actions.append({
                    "source_id": source_id,
                    "action": "recovery",
                    "webhook": result,
                })
            else:
                actions.append({
                    "source_id": source_id,
                    "action": "recovery",
                    "webhook": {"ok": True, "dry_run": True} if dry_run else {"ok": False, "error": "no webhook"},
                })

        # unknown → ok/stale/error: treat as new, don't alert
        # (first check after startup shouldn't fire)

        # Update state
        state[source_id] = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    _save_alert_state(state)
    return actions


def get_alert_state() -> dict:
    """Return the current alert state."""
    return _load_alert_state()


def reset_alert_state() -> None:
    """Clear all alert state (useful for testing)."""
    _save_alert_state({})
