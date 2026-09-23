"""Incident model — durable incident tracking for source failures.

Incidents track the lifecycle of a problem:
  open → updating → resolved

Each incident has a stable ID and append-only event log.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import STATE_DIR


INCIDENTS_DIR = STATE_DIR / "incidents"


def _ensure_dir():
    INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)


def _incident_path(incident_id: str) -> Path:
    return INCIDENTS_DIR / f"{incident_id}.json"


def create_incident(
    source_id: str,
    garden: str,
    severity: str,
    reason: str,
    last_success: Optional[str] = None,
    error: Optional[str] = None,
) -> dict:
    """Create a new incident."""
    _ensure_dir()
    now = datetime.now(timezone.utc).isoformat()
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    incident_id = f"inc-{date_str}-{garden}-{source_id}"

    incident = {
        "incident_id": incident_id,
        "source_id": source_id,
        "garden": garden,
        "opened_at": now,
        "resolved_at": None,
        "status": "open",
        "severity": severity,
        "reason": reason,
        "last_success": last_success,
        "current_error": error,
        "events": [
            {
                "at": now,
                "type": "opened",
                "severity": severity,
                "reason": reason,
                "error": error,
            }
        ],
    }

    path = _incident_path(incident_id)
    with open(path, "w") as f:
        json.dump(incident, f, indent=2)

    return incident


def update_incident(
    incident_id: str,
    severity: Optional[str] = None,
    reason: Optional[str] = None,
    error: Optional[str] = None,
) -> Optional[dict]:
    """Update an existing incident."""
    path = _incident_path(incident_id)
    if not path.exists():
        return None

    with open(path) as f:
        incident = json.load(f)

    now = datetime.now(timezone.utc).isoformat()

    if severity:
        incident["severity"] = severity
    if reason:
        incident["reason"] = reason
    if error is not None:
        incident["current_error"] = error

    event = {"at": now, "type": "updated"}
    if severity:
        event["severity"] = severity
    if reason:
        event["reason"] = reason
    if error is not None:
        event["error"] = error

    incident["events"].append(event)

    with open(path, "w") as f:
        json.dump(incident, f, indent=2)

    return incident


def resolve_incident(incident_id: str) -> Optional[dict]:
    """Resolve an incident."""
    path = _incident_path(incident_id)
    if not path.exists():
        return None

    with open(path) as f:
        incident = json.load(f)

    now = datetime.now(timezone.utc).isoformat()
    incident["resolved_at"] = now
    incident["status"] = "resolved"
    incident["events"].append({
        "at": now,
        "type": "resolved",
    })

    with open(path, "w") as f:
        json.dump(incident, f, indent=2)

    return incident


def get_incidents(
    status: Optional[str] = None,
    garden: Optional[str] = None,
    source_id: Optional[str] = None,
) -> list[dict]:
    """Query incidents with optional filters."""
    _ensure_dir()
    incidents = []
    for p in INCIDENTS_DIR.glob("inc-*.json"):
        try:
            with open(p) as f:
                incident = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if status and incident.get("status") != status:
            continue
        if garden and incident.get("garden") != garden:
            continue
        if source_id and incident.get("source_id") != source_id:
            continue

        incidents.append(incident)

    incidents.sort(key=lambda i: i.get("opened_at", ""), reverse=True)
    return incidents


def get_open_incidents(garden: Optional[str] = None) -> list[dict]:
    """Get all open incidents."""
    return get_incidents(status="open", garden=garden)


def find_open_incident(source_id: str) -> Optional[dict]:
    """Find an open incident for a specific source."""
    incidents = get_incidents(status="open", source_id=source_id)
    return incidents[0] if incidents else None
