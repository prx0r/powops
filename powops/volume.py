"""Volume tracking — row count history and anomaly detection.

Records per-source row counts on each check, computes rolling
statistics, and flags anomalies (sudden drops or spikes).
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from .garden import SourceStatus
from .config import VOLUME_DIR


def _ensure_volume_dir():
    VOLUME_DIR.mkdir(parents=True, exist_ok=True)


def record_volume(results: List[SourceStatus]) -> None:
    """Record row counts for each source to today's volume file."""
    _ensure_volume_dir()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = VOLUME_DIR / f"{today}.jsonl"

    now = datetime.now(timezone.utc).isoformat()
    with open(path, "a") as f:
        for r in results:
            if r.records is not None:
                entry = {
                    "ts": now,
                    "source_id": r.source_id,
                    "garden": r.garden,
                    "records": r.records,
                }
                f.write(json.dumps(entry) + "\n")


def get_volume_history(
    source_id: str,
    days: int = 14,
) -> List[dict]:
    """Get row count history for a source."""
    _ensure_volume_dir()
    entries = []
    now = datetime.now(timezone.utc)

    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = VOLUME_DIR / f"{date}.jsonl"
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            e = json.loads(line)
                            if e.get("source_id") == source_id:
                                entries.append(e)
                        except json.JSONDecodeError:
                            continue

    entries.sort(key=lambda e: e.get("ts", ""))
    return entries


def compute_rolling_stats(values: List[int]) -> dict:
    """Compute rolling statistics from a list of values.

    Returns mean, stddev, min, max, and count.
    """
    if not values:
        return {"mean": 0, "stddev": 0, "min": 0, "max": 0, "count": 0}

    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n if n > 1 else 0
    stddev = variance ** 0.5

    return {
        "mean": round(mean),
        "stddev": round(stddev),
        "min": min(values),
        "max": max(values),
        "count": n,
    }


def detect_volume_anomaly(
    source_id: str,
    current_records: int,
    days: int = 7,
    drop_threshold: float = 0.5,
    spike_threshold: float = 3.0,
    min_samples: int = 3,
) -> Optional[dict]:
    """Detect if current record count is anomalous.

    Args:
        source_id: Source to check
        current_records: Current row count
        days: Rolling window size
        drop_threshold: Alert if current < mean * this (e.g. 0.5 = 50% of mean)
        spike_threshold: Alert if current > mean * this (e.g. 3.0 = 300% of mean)
        min_samples: Need at least this many historical samples

    Returns:
        None if normal, or dict with anomaly details
    """
    entries = get_volume_history(source_id, days=days)

    # Extract the most recent entry per day (take the latest)
    daily_max = {}
    for e in entries:
        date = e.get("ts", "")[:10]
        daily_max[date] = e.get("records", 0)

    # Use values from the last N days (excluding today)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    historical = [v for d, v in daily_max.items() if d != today and v is not None]

    if len(historical) < min_samples:
        return None  # Not enough data

    stats = compute_rolling_stats(historical)
    mean = stats["mean"]
    if mean == 0:
        return None

    ratio = current_records / mean

    if ratio < drop_threshold:
        return {
            "type": "drop",
            "source_id": source_id,
            "current": current_records,
            "mean": mean,
            "ratio": round(ratio, 2),
            "threshold": drop_threshold,
            "message": f"Row count dropped to {ratio:.0%} of average ({current_records:,} vs {mean:,})",
        }
    elif ratio > spike_threshold:
        return {
            "type": "spike",
            "source_id": source_id,
            "current": current_records,
            "mean": mean,
            "ratio": round(ratio, 2),
            "threshold": spike_threshold,
            "message": f"Row count spiked to {ratio:.0%} of average ({current_records:,} vs {mean:,})",
        }

    return None


def get_volume_summary(days: int = 7) -> dict:
    """Get volume summary for all sources."""
    _ensure_volume_dir()
    source_ids = set()
    now = datetime.now(timezone.utc)

    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = VOLUME_DIR / f"{date}.jsonl"
        if path.exists():
            with open(path) as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        source_ids.add(e.get("source_id", ""))
                    except (json.JSONDecodeError, AttributeError):
                        continue

    summary = {}
    for sid in sorted(source_ids):
        if not sid:
            continue
        history = get_volume_history(sid, days=days)
        values = [e.get("records", 0) for e in history if e.get("records") is not None]
        if values:
            summary[sid] = compute_rolling_stats(values)

    return summary
