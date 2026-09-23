"""Garden discovery and per-garden health readers.

Each garden produces health artifacts in its own format:
- powpowpow: heartbeat JSON files, daemon PID
- repair: SQLite collector_run table
- powuk: raw directory file mtimes
- powstock: heartbeat JSON files (when it exists)

This module reads those artifacts and returns a uniform SourceStatus.
"""

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Server secret — generated at import time, never changes within a process.
# Used to sign check results so timestamps can't be faked.
_SERVER_SECRET = os.urandom(32).hex()


def _compute_check_hash(source_id: str, status: str, checked_at: str) -> str:
    """Compute HMAC signature for a check result.

    Proves the server actually checked this source at this time.
    Cannot be forged without the server secret.
    """
    payload = f"{source_id}:{status}:{checked_at}"
    return hashlib.sha256(
        (_SERVER_SECRET + payload).encode()
    ).hexdigest()[:32]


@dataclass
class SourceStatus:
    """Uniform health status for a single data source."""
    source_id: str
    garden: str
    authority: str
    description: str
    status: str  # ok, stale, blocked, no_key, not_installed, error, unknown
    checked_at: Optional[datetime] = None  # when powops checked this source (server-side)
    last_attempt: Optional[datetime] = None  # when we last tried to collect
    last_success: Optional[datetime] = None  # when we last got valid data
    age: Optional[timedelta] = None
    records: Optional[int] = None
    error: Optional[str] = None
    check_hash: Optional[str] = None  # HMAC of (source_id + status + checked_at) — proves server checked
    evidence_level: str = "weak"  # weak (mtime/pid), strong (heartbeat/collector_db with data)
    details: dict = field(default_factory=dict)

    def to_verified_dict(self) -> dict:
        """Convert to dict with verified timestamps."""
        d = {
            "source_id": self.source_id,
            "garden": self.garden,
            "authority": self.authority,
            "description": self.description,
            "status": self.status,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
            "last_attempt": self.last_attempt.isoformat() if self.last_attempt else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "age_seconds": int(self.age.total_seconds()) if self.age is not None else None,
            "records": self.records,
            "error": self.error,
            "check_hash": self.check_hash,
            "evidence_level": self.evidence_level,
        }
        return d


def _parse_duration(s: str) -> timedelta:
    """Parse a human duration like '10m', '2h', '48h', '300s' into timedelta."""
    s = s.strip().lower()
    if s.endswith("s"):
        return timedelta(seconds=int(s[:-1]))
    elif s.endswith("m"):
        return timedelta(minutes=int(s[:-1]))
    elif s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    elif s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    return timedelta(minutes=10)


def _parse_ts(ts_str: str) -> Optional[datetime]:
    """Parse an ISO timestamp string into a timezone-aware datetime."""
    if not ts_str:
        return None
    try:
        # Handle Z suffix
        ts_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _age_since(dt: Optional[datetime]) -> Optional[timedelta]:
    """Compute age since a datetime, or None."""
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    return now - dt


class GardenReader:
    """Reads health artifacts from a specific garden."""

    def __init__(self, garden_id: str, garden_config: dict):
        self.garden_id = garden_id
        self.path = Path(garden_config["path"])
        self.config = garden_config

    def exists(self) -> bool:
        return self.path.exists() and self.path.is_dir()

    def read_heartbeat(self, health_config: dict) -> SourceStatus:
        """Read a heartbeat JSON file and compute status."""
        heartbeat_path = self.path / health_config["file"]
        max_staleness = _parse_duration(health_config.get("max_staleness", "10m"))

        if not heartbeat_path.exists():
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"Heartbeat file not found: {heartbeat_path}",
            )

        try:
            with open(heartbeat_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"Failed to read heartbeat: {e}",
            )

        heartbeat_at = _parse_ts(data.get("heartbeat_at", ""))

        # Reject missing, empty or unparseable timestamps
        if heartbeat_at is None:
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"Heartbeat missing or unparseable heartbeat_at: {heartbeat_path}",
            )

        # Reject implausibly future-dated timestamps (>5min ahead)
        now = datetime.now(timezone.utc)
        if heartbeat_at > now + timedelta(minutes=5):
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"Heartbeat timestamp is in the future: {heartbeat_at.isoformat()}",
            )

        age = _age_since(heartbeat_at)
        is_stale = age is not None and age > max_staleness

        # Extract stats
        stats = {k: v for k, v in data.items() if k != "heartbeat_at" and k != "mode"}

        return SourceStatus(
            source_id="", garden=self.garden_id,
            authority="", description="",
            status="stale" if is_stale else "ok",
            last_success=heartbeat_at,
            age=age,
            evidence_level="strong",
            details=stats,
        )

    def read_collector_db(self, health_config: dict) -> SourceStatus:
        """Query the repair-style collector_run table."""
        db_path = self.path / self.config.get("db_path", "warehouse/repair.db")
        source_id = health_config.get("source_id", "")
        max_staleness = _parse_duration(health_config.get("max_staleness", "24h"))

        if not db_path.exists():
            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"Database not found: {db_path}",
            )

        try:
            conn = sqlite3.connect(str(db_path))
            # Try collector_run first, then collection_runs (repair uses the latter)
            row = None
            for table in ("collector_run", "collection_runs"):
                try:
                    if table == "collector_run":
                        row = conn.execute(
                            """SELECT started_at, status, error, duration_seconds,
                                      source_records_new, raw_new
                               FROM collector_run
                               WHERE source_id = ?
                               ORDER BY run_id DESC LIMIT 1""",
                            (source_id,),
                        ).fetchone()
                    else:
                        row = conn.execute(
                            """SELECT started_at, status, error, duration_seconds,
                                      rows_collected, rows_inserted
                               FROM collection_runs
                               WHERE source_id = ?
                               ORDER BY id DESC LIMIT 1""",
                            (source_id,),
                        ).fetchone()
                    if row is not None:
                        break
                except sqlite3.OperationalError:
                    continue
            conn.close()
        except sqlite3.Error as e:
            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"DB query failed: {e}",
            )

        if row is None:
            # Fallback: check raw directory mtime for this source
            raw_dir = self.path / "warehouse" / "raw" / source_id
            if raw_dir.exists():
                newest_mtime = None
                for fname in os.listdir(raw_dir):
                    fpath = raw_dir / fname
                    try:
                        mt = os.path.getmtime(fpath)
                        if newest_mtime is None or mt > newest_mtime:
                            newest_mtime = mt
                    except OSError:
                        continue
                if newest_mtime is not None:
                    last_good = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)
                    age = _age_since(last_good)
                    is_stale = age is not None and age > max_staleness
                    return SourceStatus(
                        source_id=source_id, garden=self.garden_id,
                        authority="", description="",
                        status="stale" if is_stale else "ok",
                        last_success=last_good,
                        age=age,
                        error="No collector_run entries (raw fallback)",
                    )

            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error="No runs recorded",
            )

        started_at, status_str, error, duration, records_new, raw_new = row
        last_attempt = _parse_ts(started_at)
        age = _age_since(last_attempt)
        is_stale = age is not None and age > max_staleness

        # For status resolution: distinguish failed attempts from successful ones.
        # "running" is treated as stale (in-progress, not yet validated).
        # "error" means the collector failed — do NOT use its timestamp as last_success.
        if status_str == "error":
            resolved = "error"
            # Do not set last_success from a failed attempt
            last_good = None
        elif is_stale:
            resolved = "stale"
            last_good = last_attempt
        elif status_str == "running":
            resolved = "stale"
            last_good = last_attempt
        else:
            resolved = "ok"
            last_good = last_attempt

        return SourceStatus(
            source_id=source_id, garden=self.garden_id,
            authority="", description="",
            status=resolved,
            last_success=last_good,
            age=age,
            records=records_new,
            error=error,
            evidence_level="strong",
            details={"db_status": status_str, "duration": duration, "raw_new": raw_new},
        )

    def read_raw_mtime(self, health_config: dict) -> SourceStatus:
        """Check file modification times in a raw directory."""
        raw_dir = self.path / health_config.get("directory", "data/raw")
        max_staleness = _parse_duration(health_config.get("max_staleness", "48h"))

        if not raw_dir.exists():
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"Raw directory not found: {raw_dir}",
            )

        # Find most recent file
        newest_mtime = None
        file_count = 0
        for root, dirs, files in os.walk(raw_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mt = os.path.getmtime(fpath)
                    file_count += 1
                    if newest_mtime is None or mt > newest_mtime:
                        newest_mtime = mt
                except OSError:
                    continue

        if newest_mtime is None:
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error="No files in raw directory",
            )

        last_good = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)
        age = _age_since(last_good)
        is_stale = age is not None and age > max_staleness

        return SourceStatus(
            source_id="", garden=self.garden_id,
            authority="", description="",
            status="stale" if is_stale else "ok",
            last_success=last_good,
            age=age,
            records=file_count,
            evidence_level="weak",
        )

    def read_pid_file(self, health_config: dict) -> SourceStatus:
        """Check if a PID file points to a live process."""
        pid_path = self.path / health_config["file"]

        if not pid_path.exists():
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error="No PID file",
            )

        try:
            pid = int(pid_path.read_text().strip())
        except (ValueError, OSError):
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="error",
                error="Invalid PID file",
            )

        try:
            os.kill(pid, 0)
            # Process is live, but we have no data-validation proof
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"Process {pid} running (no data validation)",
                evidence_level="weak",
                details={"pid": pid},
            )
        except ProcessLookupError:
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="stale",
                error=f"Process {pid} not running (stale PID)",
                evidence_level="weak",
            )
        except PermissionError:
            return SourceStatus(
                source_id="", garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"Process {pid} running but not accessible",
                evidence_level="weak",
                details={"pid": pid},
            )

    def read_pow_health(self, source_id: str, health_config: dict) -> SourceStatus:
        """Read a pow-health/1 JSON artifact emitted by a garden collector.

        The artifact is at <garden_path>/data/health/{source_id}.json
        This is the preferred health check — strong evidence, structured data.
        """
        health_dir = self.path / health_config.get("directory", "data/health")
        artifact_path = health_dir / f"{source_id}.json"
        max_staleness = _parse_duration(health_config.get("max_staleness", "48h"))

        if not artifact_path.exists():
            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="unknown",
                error=f"No health artifact: {artifact_path}",
            )

        try:
            with open(artifact_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"Failed to read health artifact: {e}",
            )

        # Validate protocol
        if data.get("protocol") != "pow-health/1":
            return SourceStatus(
                source_id=source_id, garden=self.garden_id,
                authority="", description="",
                status="error",
                error=f"Unknown protocol: {data.get('protocol')}",
            )

        last_attempt = _parse_ts(data.get("last_attempt"))
        last_success = _parse_ts(data.get("last_success"))
        attempt_status = data.get("attempt_status", "error")
        error = data.get("error")

        # Determine health from attempt_status + staleness
        age = _age_since(last_success)
        is_stale = age is not None and age > max_staleness

        if attempt_status == "blocked":
            resolved = "blocked"
        elif attempt_status == "error" or error:
            resolved = "error"
        elif is_stale:
            resolved = "stale"
        else:
            resolved = "ok"

        # Extract stats from artifact
        records = data.get("records_seen")
        records_new = data.get("records_new")
        coverage_ratio = data.get("coverage_ratio")
        expected_count = data.get("expected_count")

        details = {}
        for k in ("records_new", "bytes_new", "schema_hash", "collector_version",
                   "raw_artifact_count", "coverage_ratio", "expected_count", "source_timestamp"):
            if k in data and data[k] is not None:
                details[k] = data[k]

        return SourceStatus(
            source_id=source_id, garden=self.garden_id,
            authority=data.get("authority", ""),
            description="",
            status=resolved,
            last_attempt=last_attempt,
            last_success=last_success if not is_stale else None,
            age=age,
            records=records,
            error=error,
            evidence_level="strong",
            details=details,
        )
