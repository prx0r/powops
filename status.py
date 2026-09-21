"""CLI status table rendering.

Renders the health status of all sources across all gardens
as a formatted terminal table using only stdlib.
"""

import sys
from datetime import timedelta
from typing import List, Optional

from .health import check_all, garden_summary, overall_status, SOURCES_YAML
from .garden import SourceStatus


# Status formatting constants
STATUS_COLORS = {
    "ok": "\033[32m",          # green
    "stale": "\033[33m",       # yellow
    "error": "\033[31m",       # red
    "blocked": "\033[31m",     # red
    "no_key": "\033[36m",      # cyan
    "not_installed": "\033[90m",  # dim
    "unknown": "\033[90m",     # dim
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

STATUS_ICONS = {
    "ok": "ok",
    "stale": "STALE",
    "error": "ERR",
    "blocked": "BLOCKED",
    "no_key": "NO_KEY",
    "not_installed": "---",
    "unknown": "?",
}


def _format_age(age: Optional[timedelta]) -> str:
    if age is None:
        return "—"
    total = int(age.total_seconds())
    if total < 60:
        return f"{total}s"
    elif total < 3600:
        return f"{total // 60}m"
    elif total < 86400:
        h = total // 3600
        m = (total % 3600) // 60
        return f"{h}h{m:02d}m"
    else:
        d = total // 86400
        h = (total % 86400) // 3600
        return f"{d}d{h}h"


def _format_ts(dt) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%H:%M")


def _colorize(text: str, status: str) -> str:
    color = STATUS_COLORS.get(status, "")
    return f"{color}{text}{RESET}" if color else text


def render_status_table(
    results: List[SourceStatus],
    use_color: bool = True,
    show_garden_header: bool = True,
) -> str:
    """Render the status table as a string."""
    if not results:
        return "No sources configured."

    lines = []
    now_str = ""
    try:
        from datetime import datetime, timezone
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        pass

    # Header
    lines.append("")
    if use_color:
        lines.append(f"{BOLD}POWOPS — Layer 1 Command Centre{RESET}  {DIM}{now_str}{RESET}")
    else:
        lines.append(f"POWOPS — Layer 1 Command Centre  {now_str}")
    lines.append("")

    # Overall status
    overall = overall_status(results)
    overall_color = {
        "all_ok": "\033[32m",
        "ok": "\033[32m",
        "partial_outage": "\033[33m",
        "degraded": "\033[31m",
        "no_data": "\033[90m",
    }.get(overall, "")
    overall_label = {
        "all_ok": "ALL SYSTEMS OPERATIONAL",
        "ok": "OPERATIONAL",
        "partial_outage": "PARTIAL OUTAGE",
        "degraded": "DEGRADED",
        "no_data": "NO DATA",
    }.get(overall, overall.upper())
    if use_color:
        lines.append(f"  Overall: {overall_color}{BOLD}{overall_label}{RESET}")
    else:
        lines.append(f"  Overall: {overall_label}")
    lines.append("")

    # Table header
    col_w = {"garden": 12, "source": 22, "last_good": 12, "age": 10, "status": 12}
    header = (
        f"  {'GARDEN':<{col_w['garden']}}"
        f"{'SOURCE':<{col_w['source']}}"
        f"{'LAST GOOD':<{col_w['last_good']}}"
        f"{'AGE':<{col_w['age']}}"
        f"{'STATUS':<{col_w['status']}}"
    )
    if use_color:
        lines.append(f"{DIM}{header}{RESET}")
    else:
        lines.append(header)
    lines.append(f"  {'─' * (col_w['garden'] + col_w['source'] + col_w['last_good'] + col_w['age'] + col_w['status'])}")

    # Group by garden
    gardens = {}
    for r in results:
        gardens.setdefault(r.garden, []).append(r)

    for garden_id, garden_results in gardens.items():
        first = True
        for r in garden_results:
            garden_label = garden_id if first else ""
            icon = STATUS_ICONS.get(r.status, "?")
            colored_status = _colorize(f"{icon:>{col_w['status']-1}}", r.status) if use_color else f"{icon:>{col_w['status']-1}}"
            age_str = _format_age(r.age)
            ts_str = _format_ts(r.last_good)

            line = (
                f"  {garden_label:<{col_w['garden']}}"
                f"{r.source_id:<{col_w['source']}}"
                f"{ts_str:<{col_w['last_good']}}"
                f"{age_str:<{col_w['age']}}"
                f"{colored_status}"
            )
            lines.append(line)
            first = False

        # Separator between gardens
        sep = "  " + "─" * (col_w['garden'] + col_w['source'] + col_w['last_good'] + col_w['age'] + col_w['status'])
        if use_color:
            lines.append(f"{DIM}{sep}{RESET}")
        else:
            lines.append(sep)

    # Summary
    gs = garden_summary(results)
    active = [r for r in results if r.status not in ("not_installed", "unknown")]
    ok_count = sum(1 for r in active if r.status == "ok")
    lines.append("")
    summary_parts = [f"{ok_count}/{len(active)} sources OK"]
    for gid, stats in gs.items():
        n_ok = stats.get("ok", 0)
        n_total = stats.get("total", 0)
        n_err = stats.get("error", 0) + stats.get("stale", 0)
        if n_err:
            summary_parts.append(f"{gid}: {n_ok}/{n_total} ok, {n_err} issues")
        else:
            summary_parts.append(f"{gid}: {n_ok}/{n_total} ok")
    summary_text = " | ".join(summary_parts)
    if use_color:
        lines.append(f"  {DIM}{summary_text}{RESET}")
    else:
        lines.append(f"  {summary_text}")
    lines.append("")

    return "\n".join(lines)


def render_json(results: List[SourceStatus]) -> str:
    """Render results as JSON."""
    import json
    from datetime import datetime, timezone

    data = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall_status(results),
        "gardens": garden_summary(results),
        "sources": [],
    }
    for r in results:
        entry = {
            "source_id": r.source_id,
            "garden": r.garden,
            "authority": r.authority,
            "status": r.status,
        }
        if r.last_good:
            entry["last_good"] = r.last_good.isoformat()
        if r.age:
            entry["age_seconds"] = int(r.age.total_seconds())
        if r.error:
            entry["error"] = r.error
        if r.records is not None:
            entry["records"] = r.records
        data["sources"].append(entry)

    return json.dumps(data, indent=2)


def run_status(use_color: bool = True, fmt: str = "table", path=None) -> None:
    """Run the status check and print results."""
    results = check_all(path)

    if fmt == "json":
        print(render_json(results))
    else:
        print(render_status_table(results, use_color=use_color))
