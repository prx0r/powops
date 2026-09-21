"""Tests for powops new modules: history, alerts, volume, schema."""

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

from powops.garden import SourceStatus
from powops.history import (
    record_check,
    get_history,
    get_source_timeline,
    get_uptime_stats,
    list_history_files,
    HISTORY_DIR,
)
from powops.alerts import (
    process_alerts,
    get_alert_state,
    reset_alert_state,
    _build_alert_payload,
    _build_recovery_payload,
    ALERT_STATE_FILE,
)
from powops.volume import (
    record_volume,
    get_volume_history,
    compute_rolling_stats,
    detect_volume_anomaly,
    get_volume_summary,
    VOLUME_DIR,
)
from powops.schema import (
    snapshot_source_schema,
    get_schema_snapshot,
    detect_schema_drift,
    check_and_update_schema,
    list_schemas,
    SCHEMA_DIR,
)


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _make_status(source_id, garden="test", status="ok", records=None, error=None):
    return SourceStatus(
        source_id=source_id,
        garden=garden,
        authority="test",
        description="test source",
        status=status,
        last_good=datetime.now(timezone.utc),
        age=timedelta(minutes=2),
        records=records,
        error=error,
    )


# ═══════════════════════════════════════════════════════════
# Test: History
# ═══════════════════════════════════════════════════════════

class TestHistory:
    def test_record_and_query(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            results = [_make_status("src_a"), _make_status("src_b")]
            record_check(results)

            entries = get_history(source_id="src_a")
            assert len(entries) == 1
            assert entries[0]["source_id"] == "src_a"
            assert entries[0]["status"] == "ok"

    def test_query_by_garden(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            results = [
                _make_status("a", garden="g1"),
                _make_status("b", garden="g2"),
            ]
            record_check(results)

            entries = get_history(garden="g1")
            assert len(entries) == 1
            assert entries[0]["garden"] == "g1"

    def test_query_by_status(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            results = [
                _make_status("a", status="ok"),
                _make_status("b", status="stale"),
            ]
            record_check(results)

            entries = get_history(status_filter="stale")
            assert len(entries) == 1
            assert entries[0]["status"] == "stale"

    def test_timeline_dedup(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            # Record 3 ok checks then 1 stale
            for _ in range(3):
                record_check([_make_status("a", status="ok")])
            record_check([_make_status("a", status="stale")])

            timeline = get_source_timeline("a")
            assert len(timeline) == 2
            assert timeline[0]["status"] == "ok"
            assert timeline[1]["status"] == "stale"

    def test_uptime_stats(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            for _ in range(8):
                record_check([_make_status("a", status="ok")])
            record_check([_make_status("a", status="stale")])

            stats = get_uptime_stats("a")
            assert stats["total_checks"] == 9
            assert stats["ok"] == 8
            assert stats["stale"] == 1
            assert stats["uptime_pct"] > 88

    def test_list_history_files(self, tmp_path):
        with mock.patch("powops.history.HISTORY_DIR", tmp_path):
            record_check([_make_status("a")])
            files = list_history_files()
            assert len(files) == 1
            assert files[0]["entries"] == 1


# ═══════════════════════════════════════════════════════════
# Test: Alerts
# ═══════════════════════════════════════════════════════════

class TestAlerts:
    def setup_method(self):
        reset_alert_state()

    def test_no_alert_on_first_check(self, tmp_path):
        with mock.patch("powops.alerts.ALERT_STATE_FILE", tmp_path / "state.json"):
            results = [_make_status("a", status="stale")]
            configs = {"a": {"enabled": True, "severity": {"stale": True}}}
            actions = process_alerts(results, configs, dry_run=True)
            # First check (unknown→stale) should NOT alert
            assert len(actions) == 0

    def test_alert_on_transition(self, tmp_path):
        with mock.patch("powops.alerts.ALERT_STATE_FILE", tmp_path / "state.json"):
            # First check: ok
            results = [_make_status("a", status="ok")]
            process_alerts(results, dry_run=True)

            # Second check: stale → should alert
            results = [_make_status("a", status="stale")]
            configs = {"a": {"enabled": True, "severity": {"stale": True}}}
            actions = process_alerts(results, configs, dry_run=True)
            assert len(actions) == 1
            assert actions[0]["action"] == "alert"

    def test_recovery_on_ok(self, tmp_path):
        with mock.patch("powops.alerts.ALERT_STATE_FILE", tmp_path / "state.json"):
            # ok → stale → ok
            process_alerts([_make_status("a", status="ok")], dry_run=True)
            process_alerts([_make_status("a", status="stale")], dry_run=True)
            actions = process_alerts([_make_status("a", status="ok")], dry_run=True)
            assert len(actions) == 1
            assert actions[0]["action"] == "recovery"

    def test_no_duplicate_alerts(self, tmp_path):
        with mock.patch("powops.alerts.ALERT_STATE_FILE", tmp_path / "state.json"):
            process_alerts([_make_status("a", status="ok")], dry_run=True)
            # stale → stale should not fire
            actions1 = process_alerts([_make_status("a", status="stale")], dry_run=True)
            actions2 = process_alerts([_make_status("a", status="stale")], dry_run=True)
            assert len(actions1) == 1
            assert len(actions2) == 0

    def test_disabled_source(self, tmp_path):
        with mock.patch("powops.alerts.ALERT_STATE_FILE", tmp_path / "state.json"):
            process_alerts([_make_status("a", status="ok")], dry_run=True)
            configs = {"a": {"enabled": False}}
            actions = process_alerts([_make_status("a", status="stale")], configs, dry_run=True)
            assert len(actions) == 0

    def test_alert_payload(self):
        payload = _build_alert_payload("src", "garden", "ok", "error")
        assert payload["event"] == "status_change"
        assert payload["severity"] == "critical"
        assert payload["new_status"] == "error"

    def test_recovery_payload(self):
        payload = _build_recovery_payload("src", "garden")
        assert payload["event"] == "recovery"
        assert payload["severity"] == "info"


# ═══════════════════════════════════════════════════════════
# Test: Volume
# ═══════════════════════════════════════════════════════════

class TestVolume:
    def test_record_and_query(self, tmp_path):
        with mock.patch("powops.volume.VOLUME_DIR", tmp_path):
            results = [_make_status("src_a", records=100)]
            record_volume(results)

            history = get_volume_history("src_a")
            assert len(history) == 1
            assert history[0]["records"] == 100

    def test_rolling_stats(self):
        stats = compute_rolling_stats([100, 200, 300])
        assert stats["mean"] == 200
        assert stats["min"] == 100
        assert stats["max"] == 300
        assert stats["count"] == 3
        assert stats["stddev"] > 0

    def test_rolling_stats_empty(self):
        stats = compute_rolling_stats([])
        assert stats["mean"] == 0
        assert stats["count"] == 0

    def test_anomaly_detection_no_data(self):
        result = detect_volume_anomaly("nonexistent", 100)
        assert result is None  # Not enough data

    def test_anomaly_detection_normal(self, tmp_path):
        with mock.patch("powops.volume.VOLUME_DIR", tmp_path):
            # Record 5 days of 1000 rows with proper timestamps
            for i in range(5):
                date = (datetime.now(timezone.utc) - timedelta(days=i+1))
                path = tmp_path / f"{date.strftime('%Y-%m-%d')}.jsonl"
                path.write_text(json.dumps({
                    "source_id": "a",
                    "records": 1000,
                    "ts": date.isoformat(),
                }) + "\n")

            result = detect_volume_anomaly("a", 1050)
            assert result is None  # Within normal range

    def test_anomaly_detection_drop(self, tmp_path):
        with mock.patch("powops.volume.VOLUME_DIR", tmp_path):
            for i in range(5):
                date = (datetime.now(timezone.utc) - timedelta(days=i+1))
                path = tmp_path / f"{date.strftime('%Y-%m-%d')}.jsonl"
                path.write_text(json.dumps({
                    "source_id": "a",
                    "records": 1000,
                    "ts": date.isoformat(),
                }) + "\n")

            result = detect_volume_anomaly("a", 100)  # 10% of mean
            assert result is not None
            assert result["type"] == "drop"

    def test_volume_summary(self, tmp_path):
        with mock.patch("powops.volume.VOLUME_DIR", tmp_path):
            results = [_make_status("a", records=100), _make_status("b", records=200)]
            record_volume(results)

            summary = get_volume_summary()
            assert "a" in summary
            assert "b" in summary


# ═══════════════════════════════════════════════════════════
# Test: Schema
# ═══════════════════════════════════════════════════════════

class TestSchema:
    def test_snapshot_and_query(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            schema = {"columns": ["price", "stock"], "types": {"price": "float"}}
            snapshot_source_schema("src_a", "garden", schema)

            snap = get_schema_snapshot("src_a")
            assert snap is not None
            assert snap["schema"]["columns"] == ["price", "stock"]

    def test_no_drift_first_time(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            schema = {"columns": ["a", "b"]}
            drift = check_and_update_schema("src", "garden", schema)
            assert drift is None

    def test_drift_on_new_column(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            check_and_update_schema("src", "garden", {"columns": ["a", "b"]})
            drift = check_and_update_schema("src", "garden", {"columns": ["a", "b", "c"]})
            assert drift is not None
            assert any(d["type"] == "columns_added" for d in drift["drifts"])

    def test_drift_on_removed_column(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            check_and_update_schema("src", "garden", {"columns": ["a", "b", "c"]})
            drift = check_and_update_schema("src", "garden", {"columns": ["a", "b"]})
            assert drift is not None
            assert any(d["type"] == "columns_removed" for d in drift["drifts"])

    def test_drift_on_type_change(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            check_and_update_schema("src", "garden", {
                "columns": ["price"],
                "types": {"price": "int"},
            })
            drift = check_and_update_schema("src", "garden", {
                "columns": ["price"],
                "types": {"price": "float"},
            })
            assert drift is not None
            assert any(d["type"] == "type_changed" for d in drift["drifts"])

    def test_list_schemas(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            check_and_update_schema("a", "g1", {"columns": ["x"]})
            check_and_update_schema("b", "g2", {"columns": ["y"]})
            schemas = list_schemas()
            assert len(schemas) == 2

    def test_schema_history(self, tmp_path):
        with mock.patch("powops.schema.SCHEMA_DIR", tmp_path):
            check_and_update_schema("a", "g", {"columns": ["x"]})
            check_and_update_schema("a", "g", {"columns": ["x", "y"]})
            from powops.schema import get_schema_history
            history = get_schema_history("a")
            assert len(history) == 2
