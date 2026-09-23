"""Health check history — append-only JSONL log of every check result.

Each check produces a line like:
{
  "ts": "2026-09-21T18:30:00Z",
  "source_id": "venue_l2",
  "garden": "powpowpow",
  "status": "ok",
  "last_success": "2026-09-21T18:28:00Z",
  "age_seconds": 120,
  "records": null,
  "error": null,
  "check_hash": "a1b2c3...",
  "chain_hash": "d4e5f6..."
}

History files are partitioned by date: history/YYYY-MM-DD.jsonl
Chain hash links each entry to the previous — tampering breaks the chain.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from .garden import SourceStatus
from .config import HISTORY_DIR

# Chain state — last hash per file, persisted across writes
_chain_state: dict = {}


def _ensure_history_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _chain_hash(prev_hash: str, entry: dict) -> str:
    """Compute chain hash linking this entry to the previous one."""
    payload = prev_hash + json.dumps(entry, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _get_last_chain_hash(path: Path) -> str:
    """Get the chain hash of the last entry in a history file."""
    if path in _chain_state:
        return _chain_state[path]
    if path.exists():
        last_line = ""
        with open(path) as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()
        if last_line:
            try:
                entry = json.loads(last_line)
                return entry.get("chain_hash", "")
            except json.JSONDecodeError:
                pass
    return ""


def record_check(results: List[SourceStatus]) -> None:
    """Append check results to today's history file with chain hashing."""
    _ensure_history_dir()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = HISTORY_DIR / f"{today}.jsonl"

    prev_hash = _get_last_chain_hash(path)
    now = datetime.now(timezone.utc).isoformat()

    with open(path, "a") as f:
        for r in results:
            entry = {
                "ts": now,
                "source_id": r.source_id,
                "garden": r.garden,
                "status": r.status,
            }
            if r.checked_at:
                entry["checked_at"] = r.checked_at.isoformat()
            if r.last_success:
                entry["last_success"] = r.last_success.isoformat()
            if r.age is not None:
                entry["age_seconds"] = int(r.age.total_seconds())
            if r.records is not None:
                entry["records"] = r.records
            if r.error:
                entry["error"] = r.error
            if r.check_hash:
                entry["check_hash"] = r.check_hash

            chain = _chain_hash(prev_hash, entry)
            entry["chain_hash"] = chain
            prev_hash = chain

            f.write(json.dumps(entry) + "\n")

    _chain_state[path] = prev_hash


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


def verify_chain(path: Path) -> dict:
    """Verify the chain hash integrity of a history file.

    Returns {"ok": True, "entries": N} if chain is valid,
    or {"ok": False, "broken_at": N, "reason": "..."} if tampered.
    """
    entries = _load_history_file(path)
    if not entries:
        return {"ok": True, "entries": 0}

    prev_hash = ""
    for i, entry in enumerate(entries):
        expected_hash = entry.get("chain_hash")
        if not expected_hash:
            return {"ok": False, "broken_at": i, "reason": "missing chain_hash"}

        # Rebuild entry without chain_hash for verification
        check_entry = {k: v for k, v in entry.items() if k != "chain_hash"}
        computed = _chain_hash(prev_hash, check_entry)

        if computed != expected_hash:
            return {
                "ok": False,
                "broken_at": i,
                "reason": f"chain hash mismatch at entry {i}",
                "expected": expected_hash,
                "computed": computed,
            }

        prev_hash = expected_hash

    return {"ok": True, "entries": len(entries)}


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
        with open(p) as f:
            lines = sum(1 for _ in f)
        files.append({
            "date": p.stem,
            "path": str(p),
            "entries": lines,
            "bytes": p.stat().st_size,
        })
    return files
