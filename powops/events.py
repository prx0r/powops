"""Event stream — append-only log of operational events.

Events are the foundation for Pi agent integration.
Each event is a JSON line in a date-partitioned file.
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import STATE_DIR


EVENTS_DIR = STATE_DIR / "events"


def _ensure_dir():
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def record_event(
    event_type: str,
    garden: str,
    source_id: Optional[str] = None,
    incident_id: Optional[str] = None,
    severity: Optional[str] = None,
    details: Optional[dict] = None,
) -> dict:
    """Record an event to the append-only stream.

    Event types:
        source_stale, source_error, source_recovered,
        schema_changed, volume_anomaly,
        incident_opened, incident_updated, incident_closed,
        backup_failed, backup_verified
    """
    _ensure_dir()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    path = EVENTS_DIR / f"{today}.jsonl"

    event_id = f"evt:{now.strftime('%Y%m%d%H%M%S')}:{secrets.token_hex(4)}"
    event = {
        "event_id": event_id,
        "at": now.isoformat(),
        "type": event_type,
        "garden": garden,
    }
    if source_id:
        event["source_id"] = source_id
    if incident_id:
        event["incident_id"] = incident_id
    if severity:
        event["severity"] = severity
    if details:
        event["details"] = details

    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event


def get_events(
    days: int = 1,
    garden: Optional[str] = None,
    source_id: Optional[str] = None,
    event_type: Optional[str] = None,
) -> list[dict]:
    """Query events from the stream."""
    _ensure_dir()
    events = []
    now = datetime.now(timezone.utc)

    for i in range(days):
        date = (now - __import__('datetime').timedelta(days=i)).strftime("%Y-%m-%d")
        path = EVENTS_DIR / f"{date}.jsonl"
        if not path.exists():
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if garden and event.get("garden") != garden:
                    continue
                if source_id and event.get("source_id") != source_id:
                    continue
                if event_type and event.get("type") != event_type:
                    continue
                events.append(event)

    events.sort(key=lambda e: e.get("at", ""), reverse=True)
    return events
