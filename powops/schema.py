"""Schema drift detection — snapshot and compare source schemas.

For each source, captures the structure of the data it produces
(columns, types, patterns) and alerts when the schema changes.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import SCHEMA_DIR


def _ensure_schema_dir():
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)


def snapshot_source_schema(
    source_id: str,
    garden: str,
    schema_info: dict,
) -> dict:
    """Save a schema snapshot for a source.

    schema_info is a dict describing the source's data shape:
    {
        "columns": ["price", "stock", "condition", "market"],
        "types": {"price": "float", "stock": "str", "condition": "str"},
        "sample_count": 305649,
        "hash": "abc123"  // optional content hash
    }
    """
    _ensure_schema_dir()
    now = datetime.now(timezone.utc)
    snapshot = {
        "source_id": source_id,
        "garden": garden,
        "snapshot_at": now.isoformat(),
        "schema": schema_info,
    }

    # Save as latest
    latest_path = SCHEMA_DIR / f"{source_id}.json"
    tmp_path = latest_path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    os.replace(tmp_path, latest_path)

    # Also append to history
    history_path = SCHEMA_DIR / f"{source_id}_history.jsonl"
    with open(history_path, "a") as f:
        f.write(json.dumps(snapshot) + "\n")

    return snapshot


def get_schema_snapshot(source_id: str) -> Optional[dict]:
    """Get the latest schema snapshot for a source."""
    path = SCHEMA_DIR / f"{source_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def detect_schema_drift(
    source_id: str,
    new_schema: dict,
) -> Optional[dict]:
    """Compare new schema against the last snapshot.

    Detects:
    - Added columns
    - Removed columns
    - Type changes
    - Hash changes (content-level drift)

    Returns None if no drift, or dict with drift details.
    """
    previous = get_schema_snapshot(source_id)
    if previous is None:
        # First time seeing this source — save snapshot, no drift
        return None

    old = previous.get("schema", {})
    drifts = []

    # Column changes
    old_cols = set(old.get("columns", []))
    new_cols = set(new_schema.get("columns", []))
    added = new_cols - old_cols
    removed = old_cols - new_cols

    if added:
        drifts.append({"type": "columns_added", "columns": sorted(added)})
    if removed:
        drifts.append({"type": "columns_removed", "columns": sorted(removed)})

    # Type changes
    old_types = old.get("types", {})
    new_types = new_schema.get("types", {})
    for col in old_types:
        if col in new_types and old_types[col] != new_types[col]:
            drifts.append({
                "type": "type_changed",
                "column": col,
                "old": old_types[col],
                "new": new_types[col],
            })

    # Content hash change
    old_hash = old.get("hash")
    new_hash = new_schema.get("hash")
    if old_hash and new_hash and old_hash != new_hash:
        drifts.append({"type": "hash_changed"})

    if not drifts:
        return None

    return {
        "source_id": source_id,
        "drifts": drifts,
        "previous_at": previous.get("snapshot_at"),
        "previous_columns": sorted(old_cols),
        "current_columns": sorted(new_cols),
    }


def check_and_update_schema(
    source_id: str,
    garden: str,
    new_schema: dict,
) -> Optional[dict]:
    """Check for drift and update the snapshot.

    This is the main entry point: call it on each check with the
    source's current schema. It compares against the last snapshot,
    saves the new one, and returns drift info if any.
    """
    drift = detect_schema_drift(source_id, new_schema)
    snapshot_source_schema(source_id, garden, new_schema)
    return drift


def list_schemas() -> list:
    """List all known schemas."""
    _ensure_schema_dir()
    schemas = []
    for p in sorted(SCHEMA_DIR.glob("*.json")):
        if "_history" in p.name:
            continue
        try:
            with open(p) as f:
                data = json.load(f)
            schemas.append({
                "source_id": data.get("source_id"),
                "garden": data.get("garden"),
                "snapshot_at": data.get("snapshot_at"),
                "columns": data.get("schema", {}).get("columns", []),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return schemas


def get_schema_history(source_id: str) -> list:
    """Get the full schema change history for a source."""
    _ensure_schema_dir()
    path = SCHEMA_DIR / f"{source_id}_history.jsonl"
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries
