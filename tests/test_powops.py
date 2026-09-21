"""Tests for powops health monitoring."""

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

from powops.garden import (
    GardenReader,
    SourceStatus,
    _parse_duration,
    _parse_ts,
    _age_since,
)
from powops.health import (
    load_manifest,
    check_source,
    check_all,
    garden_summary,
    overall_status,
)
from powops.status import (
    render_status_table,
    render_json,
    _format_age,
)


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _make_heartbeat(path: Path, heartbeat_at: str = None, **extra):
    """Write a heartbeat JSON file."""
    if heartbeat_at is None:
        heartbeat_at = datetime.now(timezone.utc).isoformat()
    data = {"heartbeat_at": heartbeat_at, **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _make_collector_db(db_path: Path, source_id: str, status: str = "ok",
                       started_at: str = None, error: str = None):
    """Create a repair-style SQLite DB with a collector_run entry."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS collector_run (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            finished_at TEXT,
            status TEXT DEFAULT 'running',
            raw_fetched INTEGER DEFAULT 0,
            raw_new INTEGER DEFAULT 0,
            source_records_new INTEGER DEFAULT 0,
            source_records_updated INTEGER DEFAULT 0,
            source_records_invalid INTEGER DEFAULT 0,
            observations_new INTEGER DEFAULT 0,
            error TEXT,
            duration_seconds REAL
        )
    """)
    if started_at is None:
        started_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO collector_run
           (source_id, started_at, status, error, source_records_new, raw_new)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (source_id, started_at, status, error, 100, 50),
    )
    conn.commit()
    conn.close()


def _make_raw_dir(raw_dir: Path, file_count: int = 5, age_seconds: int = 60):
    """Create raw files with controlled mtimes."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().timestamp()
    for i in range(file_count):
        fpath = raw_dir / f"event_{i}.json"
        fpath.write_text("{}")
        # Set mtime to now - age_seconds + i (so newest is at age_seconds)
        os.utime(fpath, (now - age_seconds + i, now - age_seconds + i))


# ═══════════════════════════════════════════════════════════
# Test: _parse_duration
# ═══════════════════════════════════════════════════════════

class TestParseDuration:
    def test_seconds(self):
        assert _parse_duration("30s") == timedelta(seconds=30)

    def test_minutes(self):
        assert _parse_duration("10m") == timedelta(minutes=10)

    def test_hours(self):
        assert _parse_duration("2h") == timedelta(hours=2)

    def test_days(self):
        assert _parse_duration("7d") == timedelta(days=7)

    def test_default(self):
        assert _parse_duration("garbage") == timedelta(minutes=10)


# ═══════════════════════════════════════════════════════════
# Test: _parse_ts
# ═══════════════════════════════════════════════════════════

class TestParseTs:
    def test_iso_with_z(self):
        dt = _parse_ts("2026-09-21T18:20:14Z")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_iso_with_offset(self):
        dt = _parse_ts("2026-09-21T18:20:14+00:00")
        assert dt is not None

    def test_none(self):
        assert _parse_ts(None) is None

    def test_empty(self):
        assert _parse_ts("") is None

    def test_invalid(self):
        assert _parse_ts("not-a-date") is None


# ═══════════════════════════════════════════════════════════
# Test: GardenReader heartbeat
# ═══════════════════════════════════════════════════════════

class TestHeartbeatRead:
    def test_fresh_heartbeat(self, tmp_path):
        _make_heartbeat(tmp_path / "hb.json")
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_heartbeat({
            "file": "hb.json",
            "max_staleness": "10m",
        })
        assert status.status == "ok"
        assert status.last_success is not None
        assert status.age is not None
        assert status.age < timedelta(minutes=1)

    def test_stale_heartbeat(self, tmp_path):
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        _make_heartbeat(tmp_path / "hb.json", heartbeat_at=old_ts)
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_heartbeat({
            "file": "hb.json",
            "max_staleness": "10m",
        })
        assert status.status == "stale"
        assert status.age > timedelta(minutes=10)

    def test_missing_file(self, tmp_path):
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_heartbeat({
            "file": "nonexistent.json",
            "max_staleness": "10m",
        })
        assert status.status == "unknown"
        assert "not found" in status.error

    def test_invalid_json(self, tmp_path):
        (tmp_path / "hb.json").write_text("not json {{{")
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_heartbeat({
            "file": "hb.json",
            "max_staleness": "10m",
        })
        assert status.status == "error"
        assert "Failed to read" in status.error


# ═══════════════════════════════════════════════════════════
# Test: GardenReader collector_db
# ═══════════════════════════════════════════════════════════

class TestCollectorDbRead:
    def test_fresh_run(self, tmp_path):
        db = tmp_path / "test.db"
        _make_collector_db(db, "open_repair", status="ok")
        reader = GardenReader("repair", {"path": str(tmp_path), "db_path": "test.db"})
        status = reader.read_collector_db({
            "source_id": "open_repair",
            "max_staleness": "48h",
        })
        assert status.status == "ok"
        assert status.source_id == "open_repair"
        assert status.records == 100

    def test_stale_run(self, tmp_path):
        db = tmp_path / "test.db"
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        _make_collector_db(db, "cex", status="ok", started_at=old_ts)
        reader = GardenReader("repair", {"path": str(tmp_path), "db_path": "test.db"})
        status = reader.read_collector_db({
            "source_id": "cex",
            "max_staleness": "1h",
        })
        assert status.status == "stale"

    def test_error_run(self, tmp_path):
        db = tmp_path / "test.db"
        _make_collector_db(db, "partsdb", status="error", error="API key expired")
        reader = GardenReader("repair", {"path": str(tmp_path), "db_path": "test.db"})
        status = reader.read_collector_db({
            "source_id": "partsdb",
            "max_staleness": "24h",
        })
        assert status.status == "error"
        assert "API key expired" in status.error

    def test_no_runs(self, tmp_path):
        db = tmp_path / "test.db"
        _make_collector_db(db, "other_source")
        reader = GardenReader("repair", {"path": str(tmp_path), "db_path": "test.db"})
        status = reader.read_collector_db({
            "source_id": "nonexistent",
            "max_staleness": "24h",
        })
        assert status.status == "unknown"
        assert "No runs" in status.error

    def test_missing_db(self, tmp_path):
        reader = GardenReader("repair", {"path": str(tmp_path), "db_path": "missing.db"})
        status = reader.read_collector_db({
            "source_id": "open_repair",
            "max_staleness": "24h",
        })
        assert status.status == "unknown"
        assert "not found" in status.error


# ═══════════════════════════════════════════════════════════
# Test: GardenReader raw_mtime
# ═══════════════════════════════════════════════════════════

class TestRawMtimeRead:
    def test_fresh_files(self, tmp_path):
        _make_raw_dir(tmp_path / "data" / "raw", file_count=5, age_seconds=30)
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_raw_mtime({
            "directory": "data/raw",
            "max_staleness": "10m",
        })
        assert status.status == "ok"
        assert status.records == 5

    def test_stale_files(self, tmp_path):
        _make_raw_dir(tmp_path / "data" / "raw", file_count=3, age_seconds=7200)
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_raw_mtime({
            "directory": "data/raw",
            "max_staleness": "10m",
        })
        assert status.status == "stale"

    def test_missing_dir(self, tmp_path):
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_raw_mtime({
            "directory": "nonexistent",
            "max_staleness": "10m",
        })
        assert status.status == "unknown"

    def test_empty_dir(self, tmp_path):
        (tmp_path / "data" / "raw").mkdir(parents=True)
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_raw_mtime({
            "directory": "data/raw",
            "max_staleness": "10m",
        })
        assert status.status == "unknown"
        assert "No files" in status.error


# ═══════════════════════════════════════════════════════════
# Test: GardenReader pid_file
# ═══════════════════════════════════════════════════════════

class TestPidFileRead:
    def test_live_pid(self, tmp_path):
        # Use our own PID (definitely alive)
        (tmp_path / "daemon.pid").write_text(str(os.getpid()))
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_pid_file({"file": "daemon.pid"})
        assert status.status == "ok"
        assert status.details["pid"] == os.getpid()

    def test_stale_pid(self, tmp_path):
        # PID 1 is usually init but might not be accessible; use a known-dead PID
        (tmp_path / "daemon.pid").write_text("999999")
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_pid_file({"file": "daemon.pid"})
        assert status.status == "stale"

    def test_missing_pid_file(self, tmp_path):
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_pid_file({"file": "daemon.pid"})
        assert status.status == "unknown"

    def test_invalid_pid_file(self, tmp_path):
        (tmp_path / "daemon.pid").write_text("not-a-pid")
        reader = GardenReader("test", {"path": str(tmp_path)})
        status = reader.read_pid_file({"file": "daemon.pid"})
        assert status.status == "error"


# ═══════════════════════════════════════════════════════════
# Test: health aggregation
# ═══════════════════════════════════════════════════════════

class TestHealthAggregation:
    def test_garden_summary(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
            SourceStatus(source_id="b", garden="g1", authority="", description="", status="stale"),
            SourceStatus(source_id="c", garden="g2", authority="", description="", status="ok"),
        ]
        gs = garden_summary(results)
        assert gs["g1"]["ok"] == 1
        assert gs["g1"]["stale"] == 1
        assert gs["g1"]["total"] == 2
        assert gs["g2"]["ok"] == 1

    def test_overall_all_ok(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
            SourceStatus(source_id="b", garden="g1", authority="", description="", status="ok"),
        ]
        assert overall_status(results) == "all_ok"

    def test_overall_degraded(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
            SourceStatus(source_id="b", garden="g1", authority="", description="", status="error"),
        ]
        assert overall_status(results) == "degraded"

    def test_overall_partial_outage(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
            SourceStatus(source_id="b", garden="g1", authority="", description="", status="stale"),
        ]
        assert overall_status(results) == "partial_outage"

    def test_overall_ignores_not_installed(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
            SourceStatus(source_id="b", garden="g2", authority="", description="", status="not_installed"),
        ]
        assert overall_status(results) == "all_ok"


# ═══════════════════════════════════════════════════════════
# Test: status rendering
# ═══════════════════════════════════════════════════════════

class TestStatusRendering:
    def test_format_age_seconds(self):
        assert _format_age(timedelta(seconds=30)) == "30s"

    def test_format_age_minutes(self):
        assert _format_age(timedelta(minutes=5)) == "5m"

    def test_format_age_hours(self):
        assert _format_age(timedelta(hours=2, minutes=30)) == "2h30m"

    def test_format_age_days(self):
        assert _format_age(timedelta(days=3, hours=5)) == "3d5h"

    def test_format_age_none(self):
        assert _format_age(None) == "—"

    def test_render_table(self):
        results = [
            SourceStatus(source_id="test_src", garden="test_garden",
                         authority="Test Auth", description="Test source",
                         status="ok",
                         last_success=datetime.now(timezone.utc),
                         age=timedelta(minutes=2)),
        ]
        table = render_status_table(results, use_color=False)
        assert "test_src" in table
        assert "test_garden" in table
        assert "ok" in table.lower() or "OK" in table

    def test_render_json(self):
        results = [
            SourceStatus(source_id="a", garden="g1", authority="", description="", status="ok"),
        ]
        output = render_json(results)
        assert '"source_id": "a"' in output
        assert '"overall"' in output


# ═══════════════════════════════════════════════════════════
# Test: manifest loading
# ═══════════════════════════════════════════════════════════

class TestManifest:
    def test_load_real_manifest(self):
        manifest = load_manifest()
        assert "gardens" in manifest
        assert "sources" in manifest
        assert len(manifest["sources"]) > 0
        assert "powpowpow" in manifest["gardens"]
        assert "repair" in manifest["gardens"]

    def test_manifest_source_fields(self):
        manifest = load_manifest()
        for source in manifest["sources"]:
            assert "id" in source
            assert "garden" in source
            assert "health" in source
            assert "check" in source["health"]
