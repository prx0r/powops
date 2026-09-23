# POWOps Repository Audit

**Date:** 2026-09-23
**Commit:** 106b071
**Purpose:** Operational control system for all POW gardens

---

## Quick start for new agents

```bash
# Run status check
cd /home/ubuntu/powops
python3 -m powops status

# Run full check (history + alerts + incidents + volume + schema)
python3 -m powops full --dry-run

# List all sources
python3 -m powops sources

# Run tests
python3 -m pytest tests/ -v

# Start dashboard
python3 web/server.py
# Opens at http://localhost:8796/?token=<TOKEN>
# Token stored in ~/.powops/dashboard_token

# GitHub status
python3 -m powops repos
```

---

## Repository structure

```
powops/
├── powops/                     # Python package (the core)
│   ├── __init__.py
│   ├── __main__.py             # CLI entry point — all commands defined here
│   ├── config.py               # Path configuration (STATE_DIR, etc.)
│   ├── garden.py               # SourceStatus + GardenReader (4 check types)
│   ├── health.py               # Cross-garden aggregation + check_all_full()
│   ├── status.py               # CLI table rendering
│   ├── history.py              # Append-only JSONL history + chain hashing
│   ├── volume.py               # Row count tracking + anomaly detection
│   ├── schema.py               # Schema drift detection
│   ├── alerts.py               # State-machine webhook alerting
│   ├── incidents.py            # Durable incident tracking
│   ├── events.py               # Append-only event stream
│   ├── repos.py                # GitHub commit/CI status via gh CLI
│   ├── backup.py               # R2 sync coordination
│   ├── mcp.py                  # MCP server for pi agent
│   └── sources.yaml            # Universal source manifest (55 sources)
├── web/
│   ├── server.py               # Stdlib HTTP server (port 8796, token-gated)
│   └── static/
│       └── index.html          # Single-file SPA dashboard
├── tests/
│   ├── test_powops.py          # Core module tests (40 tests)
│   ├── test_new_features.py    # History/alerts/volume/schema tests (28 tests)
│   └── test_mcp.py             # MCP integration test (1 test)
├── deploy/
│   └── systemd/
│       ├── powops-dashboard.service
│       ├── powops-health.service
│       └── powops-health.timer
├── reports/
│   └── baseline/
│       ├── vps-audit.md        # Full VPS inventory
│       ├── garden-status.md    # Per-garden collection status
│       └── blockers.md         # All blockers by garden
├── vision/                     # Strategy documents
│   ├── README.md               # Index
│   ├── devplan.md              # START HERE — development plan
│   ├── goldmoat.md             # The flywheel
│   ├── goldmoat2.md            # Spare parts + vibecoding backend
│   ├── powvision.md            # Core thesis
│   ├── robotprintify.md        # Consumer products
│   ├── commercial.md           # 20 products
│   ├── commercial2.md          # Business model
│   ├── shopifygoat.md          # E-commerce intelligence
│   ├── nextsteps.md            # Robot parts focus
│   ├── roadmap.md              # Mission control phases
│   └── ministar.md             # Immediate priorities
├── PROGRESS.md                 # All changes documented
├── PEER_REVIEW.md              # Original code review
├── README.md                   # User-facing docs
├── overview.md                 # Architecture overview
└── pyproject.toml              # Package config
```

---

## Module responsibilities

### Core pipeline (runs in order during `powops full`)

1. **health.py** → `check_all()` reads sources.yaml, dispatches to garden.py readers
2. **garden.py** → `GardenReader` reads health artifacts from each garden (4 check types)
3. **history.py** → `record_check()` appends results to JSONL with chain hashing
4. **volume.py** → `record_volume()` tracks row counts per source
5. **alerts.py** → `process_alerts()` fires webhooks on state transitions (ok→error, error→ok)
6. **incidents.py** → Creates/updates/resolves incidents on status changes
7. **events.py** → Records all state changes to append-only event stream
8. **schema.py** → Detects schema drift (optional, only if source provides schema info)
9. **volume.py** → `detect_volume_anomaly()` flags unusual row count changes

### Supporting modules

- **config.py** — Centralizes all paths (STATE_DIR, HISTORY_DIR, etc.)
- **status.py** — Renders status tables and JSON output
- **repos.py** — GitHub commit/CI status via `gh` CLI
- **backup.py** — R2 sync coordination (reads paths from sources.yaml)
- **mcp.py** — MCP server exposing all read functions as tools

### Web dashboard

- **server.py** — Stdlib HTTP server with 12 API endpoints
- **index.html** — SPA with 9 tabs: status, history, uptime, volume, schemas, alerts, incidents, events, repos

---

## Health check types

| Type | How it works | Evidence level |
|------|-------------|---------------|
| `heartbeat` | Reads JSON file, checks `heartbeat_at` timestamp | strong |
| `collector_db` | Queries SQLite `collector_run` table | strong |
| `raw_mtime` | Checks file modification times in directory | weak |
| `pid_file` | Checks if PID file points to live process | weak |
| `pow_health` | Reads `data/health/{source}.json` artifacts | strong |

---

## CLI commands

| Command | Description |
|---------|-------------|
| `powops status` | Table view of all sources |
| `powops status --json` | JSON output |
| `powops full` | Check + history + alerts + incidents + volume |
| `powops full --dry-run` | Check without firing alerts |
| `powops history` | Recent check history |
| `powops uptime` | Uptime statistics per source |
| `powops volume` | Row count summary |
| `powops schemas` | Known schema snapshots |
| `powops alerts` | Current alert state |
| `powops incidents` | Show incidents |
| `powops events` | Show recent events |
| `powops repos` | GitHub repo status |
| `powops check <source>` | Check one source |
| `powops sources` | List all configured sources |
| `powops backup` | Sync raw data to R2 |

---

## MCP tools

| Tool | Description |
|------|-------------|
| `powops_status` | Health of all sources |
| `powops_source` | Health of one source |
| `powops_history` | Check history |
| `powops_uptime` | Uptime stats |
| `powops_timeline` | Status transitions |
| `powops_volume` | Volume summary |
| `powops_volume_source` | Volume for one source |
| `powops_incidents` | Query incidents |
| `powops_coverage` | Coverage across gardens |
| `powops_schemas` | Known schemas |
| `powops_schema` | Schema for one source |
| `powops_schema_history` | Schema change history |
| `powops_verify` | Verify chain hash integrity |
| `powops_sources` | List all sources |
| `powops_events` | Query events |
| `powops_alerts` | Current alert state |
| `powops_repos` | GitHub status |

---

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard SPA |
| `GET /api/health` | Liveness check |
| `GET /api/status` | Live health (30s cache) |
| `GET /api/history` | Check history |
| `GET /api/timeline` | Status transitions |
| `GET /api/uptime` | Uptime stats |
| `GET /api/volume` | Volume summary |
| `GET /api/volume/<src>` | Volume for one source |
| `GET /api/schemas` | Known schemas |
| `GET /api/schema/<src>` | Schema for one source |
| `GET /api/alerts` | Alert state |
| `GET /api/incidents` | Incidents |
| `GET /api/events` | Events |
| `GET /api/repos` | GitHub status |

All endpoints require `?token=<TOKEN>`.

---

## sources.yaml structure

```yaml
alerting:
  enabled: true
  default_webhook: null

gardens:
  powpowpow:
    path: /home/ubuntu/powpowpow
    health_check: heartbeat_files
  repair:
    path: /home/ubuntu/repair
    health_check: collector_db
  powuk:
    path: /home/ubuntu/powuk
  powstock:
    path: /home/ubuntu/powstock
  powproducts:
    path: /home/ubuntu/powproducts
  powrobots:
    path: /home/ubuntu/powrobots
  powphysical:
    path: /home/ubuntu/powphysical

sources:
  - id: chain_state
    garden: powpowpow
    health:
      check: heartbeat
      file: warehouse/chain_state_heartbeat.json
      max_staleness: 10m
```

---

## State directory

```
~/.powops/
├── dashboard_token          # Auth token
├── history/                 # Check history (YYYY-MM-DD.jsonl)
├── volume/                  # Volume tracking (YYYY-MM-DD.jsonl)
├── schemas/                 # Schema snapshots
├── alerts.json              # Alert state machine
├── incidents/               # Incident files
└── events/                  # Event stream (YYYY-MM-DD.jsonl)
```

---

## Tests

```bash
python3 -m pytest tests/ -v          # Run all 69 tests
python3 -m pytest tests/test_powops.py -v  # Core tests only
```

---

## Deployment

```bash
# Install
pip install -e .

# Systemd
cp deploy/systemd/*.service ~/.config/systemd/user/
cp deploy/systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable powops-dashboard.service
systemctl --user enable powops-health.timer
systemctl --user start powops-dashboard.service
systemctl --user start powops-health.timer
```

---

## Key design decisions

1. **Health artifacts** — Each garden writes `data/health/{source}.json` with `pow-health/1` protocol. powops reads these.
2. **Chain hashing** — History entries are linked by SHA256 hashes. Tampering breaks the chain.
3. **Evidence levels** — `strong` (heartbeat, collector_db, pow_health) vs `weak` (raw_mtime, pid_file).
4. **Incidents** — Lifecycle: ok→stale/error opens incident, error→ok resolves it. Filenames use `inc-` prefix.
5. **Events** — Append-only stream recording all state transitions.
6. **No economics** — powops monitors data flow, not business logic.
