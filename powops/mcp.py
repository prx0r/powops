"""POWOPS MCP Server — Layer 1 observability for the pi agent.

Provides tools for monitoring garden health, querying history,
running diagnostics, and checking data stream freshness.

All timestamps are server-signed with check_hash — cannot be faked.

Usage:
    python3 -m powops.mcp
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from powops.health import check_all, garden_summary, overall_status
from powops.history import get_history, get_source_timeline, get_uptime_stats, verify_chain
from powops.volume import get_volume_summary, get_volume_history
from powops.schema import list_schemas, get_schema_snapshot, get_schema_history
from powops.alerts import get_alert_state
from powops.incidents import get_incidents, get_open_incidents
from powops.events import get_events
from powops.repos import get_all_repos
from powops.config import STATE_DIR, HISTORY_DIR

MANIFEST = os.path.join(ROOT, "powops", "sources.yaml")

mcp = MCPServer("powops")


async def _run_sync(fn, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(None, lambda: fn(*args, **kwargs))


# ─── Health ───────────────────────────────────────────────

@mcp.tool()
async def powops_status(garden: str = "") -> str:
    """Check health of all POW data sources. Returns server-verified status with check_hash per source.

    Args:
        garden: Filter to one garden (powpowpow, repair, powuk, powstock)
    """
    results = await _run_sync(check_all, MANIFEST)
    if garden:
        results = [r for r in results if r.garden == garden]
    sources = [r.to_verified_dict() for r in results]
    gs = await _run_sync(garden_summary, results)
    return json.dumps({
        "overall": overall_status(results),
        "sources": sources,
        "gardens": gs,
    }, indent=2)


@mcp.tool()
async def powops_source(source_id: str) -> str:
    """Check a specific data source by ID. Returns detailed verified health.

    Args:
        source_id: Source ID to check (e.g. chain_state, open_repair, neso_demand)
    """
    results = await _run_sync(check_all, MANIFEST)
    match = [r for r in results if r.source_id == source_id]
    if not match:
        return json.dumps({"error": f"source '{source_id}' not found"})
    return json.dumps(match[0].to_verified_dict(), indent=2)


# ─── History & Uptime ─────────────────────────────────────

@mcp.tool()
async def powops_history(source: str = "", garden: str = "", days: int = 1) -> str:
    """Query health check history with chain hashes for tamper detection.

    Args:
        source: Filter to one source
        garden: Filter to one garden
        days: Days back (default 1)
    """
    entries = await _run_sync(
        get_history,
        source_id=source or None,
        garden=garden or None,
        days=days,
    )
    return json.dumps({
        "count": len(entries),
        "entries": entries[-50:],
    }, indent=2)


@mcp.tool()
async def powops_uptime(days: int = 7) -> str:
    """Get uptime statistics per source. Shows check count, uptime percentage, and mean age.

    Args:
        days: Days back (default 7)
    """
    results = await _run_sync(check_all, MANIFEST)
    stats = {}
    for r in results:
        if r.status != "not_installed":
            stats[r.source_id] = await _run_sync(get_uptime_stats, r.source_id, days=days)
    return json.dumps({"days": days, "sources": stats}, indent=2)


# ─── Incidents ────────────────────────────────────────────

@mcp.tool()
async def powops_incidents(status: str = "open", garden: str = "") -> str:
    """Query incidents. Shows open, resolved, or all incidents across gardens.

    Args:
        status: Filter by status — "open", "resolved", or "all" (default "open")
        garden: Filter to one garden
    """
    if status == "all":
        incidents = await _run_sync(get_incidents, garden=garden or None)
    else:
        incidents = await _run_sync(get_incidents, status=status, garden=garden or None)
    return json.dumps({"count": len(incidents), "incidents": incidents}, indent=2)


# ─── Coverage ─────────────────────────────────────────────

@mcp.tool()
async def powops_coverage() -> str:
    """Show coverage across all gardens — how many sources are installed, healthy, blocked, or missing."""
    results = await _run_sync(check_all, MANIFEST)
    gardens = {}
    for r in results:
        if r.garden not in gardens:
            gardens[r.garden] = {"installed": 0, "healthy": 0, "stale": 0, "error": 0, "unknown": 0, "not_installed": 0}
        g = gardens[r.garden]
        g["installed"] += 1
        if r.status == "ok":
            g["healthy"] += 1
        elif r.status == "stale":
            g["stale"] += 1
        elif r.status == "error":
            g["error"] += 1
        elif r.status == "unknown":
            g["unknown"] += 1
        elif r.status == "not_installed":
            g["not_installed"] += 1
    total = len(results)
    healthy = sum(1 for r in results if r.status == "ok")
    return json.dumps({
        "total": total,
        "healthy": healthy,
        "health_pct": round(100 * healthy / total, 1) if total else 0,
        "gardens": gardens,
    }, indent=2)


# ─── Schemas ──────────────────────────────────────────────

@mcp.tool()
async def powops_schemas() -> str:
    """List known schema snapshots across all sources."""
    schemas = await _run_sync(list_schemas)
    return json.dumps({"count": len(schemas), "schemas": schemas}, indent=2)


# ─── Verify ───────────────────────────────────────────────

@mcp.tool()
async def powops_verify(days: int = 1) -> str:
    """Verify chain hash integrity of history files. Detects tampering.

    Args:
        days: Days back to verify (default 1)
    """
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    results = []
    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = HISTORY_DIR / f"{date}.jsonl"
        if path.exists():
            result = await _run_sync(verify_chain, path)
            result["date"] = date
            results.append(result)
    ok = all(r["ok"] for r in results)
    return json.dumps({"verified": ok, "files": results}, indent=2)


# ─── Sources ──────────────────────────────────────────────

@mcp.tool()
async def powops_sources() -> str:
    """List all configured data sources across all gardens with their authority and cadence."""
    results = await _run_sync(check_all, MANIFEST)
    sources = [r.to_verified_dict() for r in results]
    return json.dumps({"sources": sources}, indent=2)


# ─── Events ───────────────────────────────────────────────

@mcp.tool()
async def powops_events(days: int = 1, garden: str = "", event_type: str = "") -> str:
    """Query recent events from the append-only event stream.

    Args:
        days: Days back (default 1)
        garden: Filter to one garden
        event_type: Filter by event type (e.g. source_stale, incident_opened)
    """
    from powops.events import get_events
    events = await _run_sync(
        get_events,
        days=days,
        garden=garden or None,
        event_type=event_type or None,
    )
    return json.dumps({"count": len(events), "events": events}, indent=2)


@mcp.tool()
async def powops_alerts() -> str:
    """Get current alert state for all sources. Shows which sources are in alerting state."""
    state = await _run_sync(get_alert_state)
    return json.dumps({"alerts": state}, indent=2)


@mcp.tool()
async def powops_volume(days: int = 7) -> str:
    """Get volume summary — row count statistics per source over time.

    Args:
        days: Days back (default 7)
    """
    summary = await _run_sync(get_volume_summary, days=days)
    return json.dumps({"days": days, "sources": summary}, indent=2)


@mcp.tool()
async def powops_volume_source(source_id: str, days: int = 14) -> str:
    """Get volume history for a specific source.

    Args:
        source_id: Source ID to look up
        days: Days back (default 14)
    """
    history = await _run_sync(get_volume_history, source_id, days=days)
    return json.dumps({"source": source_id, "days": days, "history": history}, indent=2)


@mcp.tool()
async def powops_timeline(source: str, days: int = 7) -> str:
    """Get status transition timeline for a source — shows when status changed.

    Args:
        source: Source ID to get timeline for
        days: Days back (default 7)
    """
    timeline = await _run_sync(get_source_timeline, source, days=days)
    return json.dumps({"source": source, "timeline": timeline}, indent=2)


@mcp.tool()
async def powops_schema(source_id: str) -> str:
    """Get the latest schema snapshot for a specific source.

    Args:
        source_id: Source ID to look up
    """
    snap = await _run_sync(get_schema_snapshot, source_id)
    if snap is None:
        return json.dumps({"error": f"no schema for {source_id}"})
    return json.dumps(snap, indent=2)


@mcp.tool()
async def powops_schema_history(source_id: str) -> str:
    """Get schema change history for a specific source.

    Args:
        source_id: Source ID to look up
    """
    history = await _run_sync(get_schema_history, source_id)
    return json.dumps({"source": source_id, "history": history}, indent=2)


@mcp.tool()
async def powops_repos() -> str:
    """Get GitHub commit and CI status for all POW repositories."""
    repos = await _run_sync(get_all_repos)
    return json.dumps({"repos": repos}, indent=2, default=str)


async def main():
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
