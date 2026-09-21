# powops

Layer 1 command centre for POW gardens.

> Are the gardens alive?

No economics. No modelling. No Seesaw. Just operational observability
across all Layer 1 data ingestion.

## Live

**https://admin.pow.systems/**

## What It Does

powops monitors every data source across every POW garden and answers one question: **is the data flowing?**

It reads health artifacts from each garden (heartbeat files, SQLite tables, file timestamps, process IDs), aggregates them into a unified status view, and tracks history, volume, schema drift, and alerts over time.

```
powpowpow  ─┐
repair     ─┤
powuk      ─┼── powops ── Dashboard (port 8796)
powstock   ─┘              CLI
                           systemd (health timer every 15min)
                           Cloudflare tunnel → admin.pow.systems
```

## Gardens

| Garden | Sources | What it collects |
|--------|---------|-----------------|
| **powpowpow** | 7 | PoW chain compute, venue L2, WebSocket ticks |
| **repair** | 7 | Open Repair, eBay UK, DVLA, land registry, planning, EPREL, France repairability |
| **powuk** | 8 | NESO demand/generation, PV Live, planning apps, ONS labour, APAR, Ofqual, contracts |
| **powstock** | 7 | Stooq/Yahoo prices, RNS, Companies House, FCA PDMR/short interest, PSC |

## Quick Start

```bash
# One-shot status check
python3 -m powops status

# Full check with history + alerts
python3 -m powops full

# List all 29 sources
python3 -m powops sources
```

## CLI Commands

```bash
python3 -m powops status              # Table view of all sources
python3 -m powops status --json       # JSON output
python3 -m powops full                # Check + record history + fire alerts
python3 -m powops full --dry-run      # Check without firing alerts
python3 -m powops history             # Recent check history
python3 -m powops history --source X  # History for one source
python3 -m powops history --garden Y  # History for one garden
python3 -m powops uptime              # Uptime stats per source
python3 -m powops volume              # Row count summary
python3 -m powops schemas             # Known schema snapshots
python3 -m powops alerts              # Current alert state
python3 -m powops check <source>      # Check one source
python3 -m powops sources             # List all configured sources
python3 -m powops backup              # Sync raw data to R2
```

## Dashboard

A single-file terminal-aesthetic SPA served by a stdlib HTTP server on port 8796.

```bash
python3 web/server.py
# Prints: http://localhost:8796/?token=<TOKEN>
```

### Views

- **STATUS** — Live health table grouped by garden
- **HISTORY** — Recent check entries, filterable by garden
- **UPTIME** — 7-day uptime percentage per source
- **VOLUME** — Row count statistics per source
- **SCHEMAS** — Known schema snapshots and drift

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Liveness check |
| `GET /api/status` | Live health check (30s cache) |
| `GET /api/history` | Check history (`?source=&garden=&days=`) |
| `GET /api/timeline` | Status transitions (`?source=&days=`) |
| `GET /api/uptime` | Uptime stats (`?days=`) |
| `GET /api/volume` | Volume summary |
| `GET /api/volume/<src>` | Volume history for one source |
| `GET /api/schemas` | Known schemas |
| `GET /api/alerts` | Current alert state |

All endpoints require `?token=<TOKEN>`. Token is auto-generated on first run and stored in `~/.powops/dashboard_token`.

## Health Check Types

Each source in `sources.yaml` has a `health.check` type:

| Type | How it works | Used by |
|------|-------------|---------|
| `heartbeat` | Reads a JSON file, checks `heartbeat_at` timestamp | powpowpow |
| `collector_db` | Queries SQLite `collector_run` or `collection_runs` table | repair |
| `raw_mtime` | Checks file modification times in a directory | powuk, powstock |
| `pid_file` | Checks if a PID file points to a live process | (available) |

## MCP Server

powops exposes an MCP server so the pi agent can autonomously monitor and troubleshoot garden health.

### Tools

| Tool | Description |
|------|-------------|
| `powops_status` | Check health of all sources (optional `garden` filter) |
| `powops_check` | Check a specific source by ID |
| `powops_history` | Query check history (optional `source`, `garden`, `days` filters) |
| `powops_uptime` | Get uptime statistics per source |
| `powops_diagnose` | Run diagnostics — identifies stale/errored sources and suggests fixes |
| `powops_sources` | List all configured sources |

### Running

```bash
python3 -m powops.mcp
```

### opencode.json config

```json
{
  "mcp": {
    "powops": {
      "type": "local",
      "command": ["python3", "-m", "powops.mcp"],
      "working_directory": "/home/ubuntu/powops",
      "enabled": true
    }
  }
}
```

### Agent workflow

The pi agent can use `powops_diagnose` to autonomously:
1. Detect stale or errored sources
2. Identify missing API keys
3. Suggest corrective actions
4. Check if collectors are running
5. Monitor uptime trends

## Architecture

```
powops/
├── powops/                  # Python package
│   ├── __main__.py          # CLI entry point
│   ├── config.py            # Path configuration (STATE_DIR, etc.)
│   ├── garden.py            # SourceStatus + GardenReader (4 check types)
│   ├── health.py            # Cross-garden aggregation + check_all_full()
│   ├── status.py            # CLI table rendering
│   ├── history.py           # Append-only JSONL history + uptime stats
│   ├── volume.py            # Row count tracking + anomaly detection
│   ├── schema.py            # Schema drift detection
│   ├── alerts.py            # State-machine webhook alerting
│   ├── mcp.py               # MCP server for pi agent
│   └── sources.yaml         # Universal source manifest
├── web/
│   ├── server.py            # Stdlib HTTP server (port 8796, token-gated)
│   └── static/
│       └── index.html       # Single-file SPA dashboard
├── deploy/
│   └── systemd/
│       ├── powops-dashboard.service   # Dashboard server
│       ├── powops-health.service      # Health snapshot (oneshot)
│       └── powops-health.timer        # Triggers health every 15min
├── tests/
│   ├── test_powops.py       # Core module tests (68 tests)
│   └── test_new_features.py # History/alerts/volume/schema tests
├── pyproject.toml
└── README.md
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POWOPS_STATE_DIR` | `~/.powops` | Runtime state directory |
| `POWOPS_TOKEN` | auto-generated | Dashboard auth token |
| `POWOPS_PORT` | `8796` | Dashboard port |

### State Directory

```
~/.powops/
├── dashboard_token          # Stable dashboard auth token
├── history/                 # Check history (YYYY-MM-DD.jsonl)
├── volume/                  # Volume tracking (YYYY-MM-DD.jsonl)
├── schemas/                 # Schema snapshots (per-source JSON)
├── alerts.json              # Alert state machine
└── health/                  # Health artifacts
```

### Source Manifest (sources.yaml)

```yaml
gardens:
  my_garden:
    path: /path/to/garden
    description: What this garden collects
    health_check: heartbeat  # or collector_db, raw_mtime, pid_file
    storage: warehouse/raw/

sources:
  - id: my_source
    garden: my_garden
    authority: Data Provider
    type: api
    description: What this source provides
    cadence: daily
    health:
      check: heartbeat
      file: warehouse/heartbeat.json
      max_staleness: 48h
```

## Adding a New Garden

1. Add the garden to `sources.yaml` under `gardens:`
2. Add its sources under `sources:`
3. If using `collector_db`, ensure the SQLite table has `started_at`, `status`, `source_id` columns
4. If using `raw_mtime`, create the `data/raw/<source>/` directory
5. Run `python3 -m powops status` — the new garden appears automatically

## Systemd Services

```bash
# Install
cp deploy/systemd/*.service ~/.config/systemd/user/
cp deploy/systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload

# Enable
systemctl --user enable powops-dashboard.service
systemctl --user enable powops-health.timer
systemctl --user enable powops-tunnel.service  # if using Cloudflare

# Start
systemctl --user start powops-dashboard.service
systemctl --user start powops-health.timer
systemctl --user start powops-tunnel.service

# Check status
systemctl --user status powops-dashboard.service
systemctl --user status powops-health.timer
journalctl --user -u powops-dashboard.service -f
```

## Tests

```bash
python3 -m pytest tests/ -v
```

68 tests covering:
- Duration and timestamp parsing
- All 4 health check types (heartbeat, collector_db, raw_mtime, pid_file)
- Health aggregation and overall status
- Status table and JSON rendering
- History recording, querying, and timeline dedup
- Volume tracking and anomaly detection
- Schema snapshot and drift detection
- Alert state machine and webhook payloads

## Design Principles

1. **No economics** — powops doesn't know what a constraint is. It knows if the data is flowing.
2. **No dependencies** — stdlib Python only (except PyYAML).
3. **Append-only** — history is never mutated, only appended.
4. **Bitemporal** — tracks both when data was collected and when it was observed.
5. **Deterministic** — same inputs produce same outputs.
6. **Boring** — simple file reads, no ML, no dashboards-within-dashboards.

## Related

- **powk** — Layer 2 dependency graph and model execution
- **powpowpow** — PoW chain compute telemetry (Layer 1)
- **repair** — Physical asset and repair telemetry (Layer 1)
- **powuk** — UK physical economy observatory (Layer 1)
- **powstock** — UK capital markets observatory (Layer 1)
