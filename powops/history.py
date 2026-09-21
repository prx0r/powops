"""Health check history — append-only JSONL log of every check result.

Each check produces a line like:
{
  "ts": "2026-09-21T18:30:00Z",
  "source_id": "venue_l2",
  "garden": "powpowpow",
  "status": "ok",
  "last_good": "2026-09-21T18:28:00Z",
  "age_seconds": 120,
  "records": null,
  "error": null
}

History files are partitioned by date: history/YYYY-MM-DD.jsonl
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from .garden import SourceStatus
from .config import HISTORY_DIR


def _ensure_history_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def record_check(results: List[SourceStatus]) -> None:
    """Append check results to today's history file."""
    _ensure_history_dir()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = HISTORY_DIR / f"{today}.jsonl"

    now = datetime.now(timezone.utc).isoformat()
    with open(path, "a") as f:
        for r in results:
            entry = {
                "ts": now,
                "source_id": r.source_id,
                "garden": r.garden,
                "status": r.status,
            }
            if r.last_good:
                entry["last_good"] = r.last_good.isoformat()
            if r.age is not None:
                entry["age_seconds"] = int(r.age.total_seconds())
            if r.records is not None:
                entry["records"] = r.records
            if r.error:
                entry["error"] = r.error
            f.write(json.dumps(entry) + "\n")


def _load_history_file(path: Path) -> List[dict]:
    """Load a single history file."""
    entries = []
    if not path.exists():
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def get_history(
    source_id: Optional[str] = None,
    garden: Optional[str] = None,
    days: int = 7,
    status_filter: Optional[str] = None,
) -> List[dict]:
    """Query recent history entries.

    Args:
        source_id: Filter to a specific source
        garden: Filter to a specific garden
        days: How many days back to look
        status_filter: Only return entries with this status
    """
    _ensure_history_dir()
    entries = []
    now = datetime.now(timezone.utc)

    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = HISTORY_DIR / f"{date}.jsonl"
        entries.extend(_load_history_file(path))

    # Apply filters
    if source_id:
        entries = [e for e in entries if e.get("source_id") == source_id]
    if garden:
        entries = [e for e in entries if e.get("garden") == garden]
    if status_filter:
        entries = [e for e in entries if e.get("status") == status_filter]

    # Sort by timestamp
    entries.sort(key=lambda e: e.get("ts", ""))
    return entries


def get_source_timeline(source_id: str, days: int = 7) -> List[dict]:
    """Get a timeline of status changes for a source.

    Deduplicates consecutive same-status entries, giving you
    the status transitions over time.
    """
    entries = get_history(source_id=source_id, days=days)
    if not entries:
        return []

    timeline = []
    last_status = None
    for e in entries:
        status = e.get("status")
        if status != last_status:
            timeline.append(e)
            last_status = status
    return timeline


def get_uptime_stats(source_id: str, days: int = 7) -> dict:
    """Compute uptime statistics for a source.

    Returns:
        {
            "total_checks": 42,
            "ok": 40,
            "stale": 1,
            "error": 1,
            "uptime_pct": 95.2,
            "mean_age_seconds": 120,
            "max_age_seconds": 3600,
        }
    """
    entries = get_history(source_id=source_id, days=days)
    if not entries:
        return {"total_checks": 0, "uptime_pct": 0.0}

    total = len(entries)
    counts = {}
    ages = []
    for e in entries:
        s = e.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
        if "age_seconds" in e:
            ages.append(e["age_seconds"])

    ok_count = counts.get("ok", 0)
    return {
        "total_checks": total,
        "ok": ok_count,
        "stale": counts.get("stale", 0),
        "error": counts.get("error", 0),
        "unknown": counts.get("unknown", 0),
        "uptime_pct": round(100 * ok_count / total, 1) if total else 0.0,
        "mean_age_seconds": round(sum(ages) / len(ages)) if ages else None,
        "max_age_seconds": max(ages) if ages else None,
    }


def list_history_files() -> List[dict]:
    """List all history files with their sizes."""
    _ensure_history_dir()
    files = []
    for p in sorted(HISTORY_DIR.glob("*.jsonl")):
        lines = sum(1 for _ in open(p))
        files.append({
            "date": p.stem,
            "path": str(p),
            "entries": lines,
            "bytes": p.stat().st_size,
        })
    return files
