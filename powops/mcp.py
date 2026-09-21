"""POWOPS MCP Server — Layer 1 observability for the pi agent.

Provides tools for monitoring garden health, querying history,
and running diagnostics across all POW data sources.

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
from mcp.types import Tool, TextContent

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from powops.health import check_all, garden_summary, overall_status
from powops.history import get_history, get_source_timeline, get_uptime_stats
from powops.volume import get_volume_summary
from powops.schema import list_schemas, get_schema_snapshot
from powops.alerts import get_alert_state
from powops.incidents import get_incidents, get_open_incidents
from powops.config import STATE_DIR

MANIFEST = os.path.join(ROOT, "powops", "sources.yaml")

mcp = MCPServer("powops")


async def _run_sync(fn, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(None, lambda: fn(*args, **kwargs))


@mcp.tool()
async def powops_status(garden: str = "") -> str:
    """Check health of all POW data sources. Returns status per source with age, garden, and overall system health.

    Args:
        garden: Filter to one garden (powpowpow, repair, powuk, powstock)
    """
    results = await _run_sync(check_all, MANIFEST)
    if garden:
        results = [r for r in results if r.garden == garden]
    sources = []
    for r in results:
        sources.append({
            "source_id": r.source_id,
            "garden": r.garden,
            "authority": r.authority,
            "status": r.status,
            "age_seconds": int(r.age.total_seconds()) if r.age is not None else None,
            "error": r.error,
        })
    gs = await _run_sync(garden_summary, results)
    return json.dumps({
        "overall": overall_status(results),
        "sources": sources,
        "gardens": gs,
    }, indent=2)


@mcp.tool()
async def powops_check(source_id: str) -> str:
    """Check a specific data source by ID. Returns detailed health for that source.

    Args:
        source_id: Source ID to check (e.g. chain_state, open_repair, neso_demand)
    """
    results = await _run_sync(check_all, MANIFEST)
    match = [r for r in results if r.source_id == source_id]
    if not match:
        return json.dumps({"error": f"source '{source_id}' not found"})
    r = match[0]
    return json.dumps({
        "source_id": r.source_id,
        "garden": r.garden,
        "authority": r.authority,
        "description": r.description,
        "status": r.status,
        "last_success": r.last_success.isoformat() if r.last_success else None,
        "age_seconds": int(r.age.total_seconds()) if r.age is not None else None,
        "records": r.records,
        "error": r.error,
    }, indent=2)


@mcp.tool()
async def powops_history(source: str = "", garden: str = "", days: int = 1) -> str:
    """Query health check history. Shows status transitions over time for sources.

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


@mcp.tool()
async def powops_diagnose() -> str:
    """Run diagnostics: identify stale sources, missing data, and suggest fixes. Returns actionable findings."""
    results = await _run_sync(check_all, MANIFEST)
    findings = []
    for r in results:
        if r.status == "stale":
            age_h = r.age.total_seconds() / 3600 if r.age else None
            findings.append({
                "severity": "warning",
                "source": r.source_id,
                "garden": r.garden,
                "issue": f"stale for {age_h:.1f}h" if age_h else "stale",
                "fix": f"check collector in {r.garden}",
            })
        elif r.status == "error":
            findings.append({
                "severity": "error",
                "source": r.source_id,
                "garden": r.garden,
                "issue": r.error or "unknown error",
                "fix": f"check logs for {r.garden}/{r.source_id}",
            })
        elif r.status == "unknown":
            findings.append({
                "severity": "info",
                "source": r.source_id,
                "garden": r.garden,
                "issue": "no data — collector may not be running",
                "fix": f"start collector for {r.source_id} in {r.garden}",
            })
        elif r.status == "no_key":
            findings.append({
                "severity": "warning",
                "source": r.source_id,
                "garden": r.garden,
                "issue": "missing API key",
                "fix": f"set required env var for {r.source_id}",
            })
    gs = await _run_sync(garden_summary, results)
    return json.dumps({
        "overall": overall_status(results),
        "findings": findings,
        "summary": gs,
    }, indent=2)


@mcp.tool()
async def powops_sources() -> str:
    """List all configured data sources across all gardens with their authority and cadence."""
    results = await _run_sync(check_all, MANIFEST)
    sources = []
    for r in results:
        sources.append({
            "id": r.source_id,
            "garden": r.garden,
            "authority": r.authority,
            "status": r.status,
        })
    return json.dumps({"sources": sources}, indent=2)


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


async def main():
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
