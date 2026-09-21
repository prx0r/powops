"""POWOPS Dashboard — Layer 1 command centre web UI.

Stdlib only. Token gate. Same pattern as powpowpow/site and qpbot/dashboard.
Binds loopback; outside world arrives via Cloudflare tunnel.

Token is stable: generated once, stored in STATE_DIR/dashboard_token.
Override with POWOPS_TOKEN env var.

API:
    GET /                    — dashboard SPA
    GET /api/health          — liveness check
    GET /api/status          — live health check (all sources, 30s cache)
    GET /api/history         — check history (optional ?source=&garden=&days=)
    GET /api/timeline        — status transitions for a source (?source=&days=)
    GET /api/uptime          — uptime stats per source (?days=)
    GET /api/volume          — volume summary (all sources)
    GET /api/volume/<src>    — volume history for one source (?days=)
    GET /api/schemas         — known schemas
    GET /api/alerts          — current alert state
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from powops.health import check_all, garden_summary, overall_status
from powops.history import get_history, get_source_timeline, get_uptime_stats
from powops.volume import get_volume_summary, get_volume_history
from powops.schema import list_schemas, get_schema_snapshot
from powops.alerts import get_alert_state
from powops.config import STATE_DIR

PORT = int(os.environ.get("POWOPS_PORT", "8796"))
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
MANIFEST = os.path.join(ROOT, "powops", "sources.yaml")


def _clamp_days(val, default=7, lo=1, hi=365):
    try:
        return max(lo, min(hi, int(val)))
    except (ValueError, TypeError):
        return default


def _get_token() -> str:
    """Get or create a stable dashboard token."""
    env_token = os.environ.get("POWOPS_TOKEN")
    if env_token:
        return env_token
    token_file = STATE_DIR / "dashboard_token"
    if token_file.exists():
        return token_file.read_text().strip()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    token = secrets.token_urlsafe(24)
    token_file.write_text(token)
    return token


TOKEN = _get_token()


class Handler(BaseHTTPRequestHandler):
    server_version = "powops-dash/0.1"

    def _gate(self) -> bool:
        q = parse_qs(urlparse(self.path).query)
        if q.get("token", [""])[0] != TOKEN:
            self._json({"error": "bad token"}, 401)
            return False
        return True

    def _headers(self):
        """Security headers for all responses."""
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'")

    def _json(self, obj, code: int = 200):
        data = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._headers()
        self.end_headers()
        self.wfile.write(data)

    def _html(self, path: str):
        with open(os.path.join(STATIC, path), "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(data)))
        self._headers()
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._gate():
            return
        u = urlparse(self.path)
        q = parse_qs(u.query)
        arg = lambda k, d="": q.get(k, [d])[0]

        # Static
        if u.path in ("/", "/index.html"):
            return self._html("index.html")

        # Health
        if u.path == "/api/health":
            return self._json({
                "ok": True,
                "time": datetime.now(timezone.utc).isoformat(),
            })

        # Live status (cached 30s)
        if u.path == "/api/status":
            try:
                return self._json(_cached_status())
            except Exception as e:
                return self._json({"error": str(e)}, 500)

        # History
        if u.path == "/api/history":
            source = arg("source") or None
            garden = arg("garden") or None
            days = _clamp_days(arg("days", "7"))
            status_f = arg("status") or None
            entries = get_history(source_id=source, garden=garden,
                                  days=days, status_filter=status_f)
            return self._json({"entries": entries, "count": len(entries)})

        # Timeline (status transitions)
        if u.path == "/api/timeline":
            source = arg("source")
            if not source:
                return self._json({"error": "missing ?source="}, 400)
            days = _clamp_days(arg("days", "7"))
            timeline = get_source_timeline(source, days=days)
            return self._json({"source": source, "timeline": timeline})

        # Uptime stats
        if u.path == "/api/uptime":
            days = _clamp_days(arg("days", "7"))
            results = check_all(MANIFEST)
            stats = {}
            for r in results:
                if r.status != "not_installed":
                    stats[r.source_id] = get_uptime_stats(r.source_id, days=days)
            return self._json({"days": days, "sources": stats})

        # Volume summary
        if u.path == "/api/volume":
            days = _clamp_days(arg("days", "7"))
            summary = get_volume_summary(days=days)
            return self._json({"days": days, "sources": summary})

        # Volume history for one source
        if u.path.startswith("/api/volume/"):
            source = u.path.split("/api/volume/", 1)[1]
            days = _clamp_days(arg("days", "14"))
            history = get_volume_history(source, days=days)
            return self._json({"source": source, "days": days, "history": history})

        # Schemas
        if u.path == "/api/schemas":
            schemas = list_schemas()
            return self._json({"schemas": schemas})

        # Schema detail
        if u.path.startswith("/api/schema/"):
            source = u.path.split("/api/schema/", 1)[1]
            snap = get_schema_snapshot(source)
            if snap:
                return self._json(snap)
            return self._json({"error": f"no schema for {source}"}, 404)

        # Alerts
        if u.path == "/api/alerts":
            state = get_alert_state()
            return self._json({"alerts": state})

        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        if not self._gate():
            return
        return self._json({"error": "not found"}, 404)

    def log_message(self, *a):
        pass


# --- 30s TTL cache for /api/status ---
_status_cache = {"data": None, "ts": 0}
_status_lock = threading.Lock()


def _cached_status() -> dict:
    now = time.time()
    if _status_cache["data"] and now - _status_cache["ts"] < 30:
        return _status_cache["data"]
    with _status_lock:
        if _status_cache["data"] and now - _status_cache["ts"] < 30:
            return _status_cache["data"]
        results = check_all(MANIFEST)
    sources = []
    for r in results:
        sources.append({
            "source_id": r.source_id,
            "garden": r.garden,
            "authority": r.authority,
            "description": r.description,
            "status": r.status,
            "last_attempt": r.last_attempt.isoformat() if r.last_attempt else None,
            "last_success": r.last_success.isoformat() if r.last_success else None,
            "age_seconds": int(r.age.total_seconds()) if r.age is not None else None,
            "records": r.records,
            "error": r.error,
        })
    gs = garden_summary(results)
    data = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall_status(results),
        "sources": sources,
        "gardens": gs,
    }
    _status_cache["data"] = data
    _status_cache["ts"] = now
    return data


if __name__ == "__main__":
    print(f"POWOps dashboard listening on 127.0.0.1:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
