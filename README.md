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
powpowpow    ─┐
repair       ─┤
powuk        ─┼── powops ── Dashboard (port 8796)
powstock     ─┤              CLI (15 commands)
powproducts  ─┤              MCP (17 tools)
powrobots    ─┤              systemd (health timer every 15min)
powphysical  ─┘              Cloudflare tunnel → admin.pow.systems
```

## Gardens (7 monitored, 88 configured sources)

| Garden | What it collects | Check types used |
|--------|-----------------|-----------------|
| **powpowpow** | PoW chain compute, venue L2, WebSocket ticks | heartbeat |
| **repair** | Open Repair, eBay/CeX, DVLA, land registry, planning, EPREL, France repairability + daemon collectors (cex, trade pricing, partsdb) | collector_db |
| **powuk** | NESO demand/generation, PV Live, planning apps, ONS labour, APAR, Ofqual, contracts | pow_health artifacts |
| **powstock** | Yahoo prices, RNS, Companies House, FCA PDMR/short interest, commodities | pow_health artifacts |
| **powproducts** | RobotShop catalogue, component identity (7 more planned) | collector_db |
| **powrobots** | HMRC trade, UKRI grants, RBTX, safety recalls, BARA, apprenticeships (+5 need API keys) | collector_db |
| **powphysical** | LCSC/M5Stack/Waveshare adapters (fixture-only, no live data yet) | raw_mtime |

Counts change as collectors are added; run `python3 -m powops sources` for the live list.

## Quick Start

```bash
# One-shot status check
python3 -m powops status

# Full check with history + alerts
python3 -m powops full

# List all configured sources
python3 -m powops sources
```

## CLI Commands

```bash
python3 -m powops status              # Table view of all sources
python3 -m powops status --json       # JSON output
python3 -m powops full                # Check + record history + fire alerts
python3 -m powops full --dry-run      # Check without firing alerts (still records history)
python3 -m powops history             # Recent check history
python3 -m powops history --source X  # History for one source
python3 -m powops history --garden Y  # History for one garden
python3 -m powops uptime              # Uptime stats per source
python3 -m powops timeline <source>   # Status transitions for one source
python3 -m powops volume              # Row count summary
python3 -m powops volume --source X   # Volume history for one source
python3 -m powops schemas             # Known schema snapshots
python3 -m powops alerts              # Current alert state
python3 -m powops incidents           # Show incidents (--status, --garden, --source)
python3 -m powops events              # Recent events (--days, --garden, --type)
python3 -m powops repos               # GitHub commit/CI status for all repos
python3 -m powops check <source>      # Check a specific source
python3 -m powops sources             # List all configured sources
python3 -m powops backup              # Sync raw data to R2
```

## Dashboard

Terminal-aesthetic SPA served by a stdlib HTTP server on port 8796.
Static assets (`style.css`, `app.js`) are separate files; CSP is strict
(no inline scripts/styles).

```bash
python3 web/server.py
# Prints: http://localhost:8796/?token=<TOKEN>
```

### Views (9 tabs)

- **STATUS** — Live health table grouped by garden
- **HISTORY** — Recent check entries, filterable by garden
- **UPTIME** — 7-day uptime percentage per source
- **VOLUME** — Row count statistics per source
- **SCHEMAS** — Known schema snapshots and drift
- **ALERTS** — Current alert state per source
- **INCIDENTS** — Open/resolved incidents
- **EVENTS** — Append-only operational event stream
- **REPOS** — GitHub commit/CI status (needs `gh auth login` on server)

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
| `GET /api/schema/<src>` | Schema snapshot for one source |
| `GET /api/alerts` | Current alert state |
| `GET /api/incidents` | Incidents (`?status=&garden=&source=`) |
| `GET /api/events` | Events (`?days=&garden=&source=&type=`) |
| `GET /api/repos` | GitHub repo status |

Auth: `?token=<TOKEN>` query param (dashboard links) or
`Authorization: Bearer <TOKEN>` header (API clients, preferred —
doesn't leak into logs). Token is auto-generated on first run and
stored in `~/.powops/dashboard_token`.

## Health Check Types

Each source in `sources.yaml` has a `health.check` type:

| Type | How it works | Evidence | Used by |
|------|-------------|----------|---------|
| `heartbeat` | Reads a JSON file, checks `heartbeat_at` timestamp (rejects missing/future) | strong | powpowpow |
| `collector_db` | Queries SQLite `collector_run` table (failed runs don't count as success) | strong | repair, powproducts, powrobots |
| `pow_health` | Reads `data/health/<source>.json` (`pow-health/1` protocol) | strong | powuk, powstock |
| `raw_mtime` | Checks file modification times in a directory | weak | powphysical |
| `pid_file` | Checks if a PID file points to a live process (live PID without data = `unknown`) | weak | (available) |

## MCP Server

powops exposes an MCP server so the pi agent can autonomously monitor and troubleshoot garden health.

### Tools (17)

| Tool | Description |
|------|-------------|
| `powops_status` | Health of all sources (optional `garden` filter) |
| `powops_source` | Health of one source by ID |
| `powops_history` | Check history (`source`, `garden`, `days`) |
| `powops_uptime` | Uptime stats per source |
| `powops_timeline` | Status transitions for one source |
| `powops_volume` | Volume summary |
| `powops_volume_source` | Volume history for one source |
| `powops_incidents` | Query incidents (`status`, `garden`) |
| `powops_coverage` | Coverage across gardens |
| `powops_schemas` | Known schemas |
| `powops_schema` | Schema snapshot for one source |
| `powops_schema_history` | Schema change history |
| `powops_verify` | Verify chain-hash integrity |
| `powops_sources` | List all configured sources |
| `powops_events` | Query event stream |
| `powops_alerts` | Current alert state |
| `powops_repos` | GitHub commit/CI status |

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

The pi agent uses the read-only tools to monitor without touching data.
A typical run: `powops_status` → `powops_incidents` → `powops_events` →
`powops_source` for anything failing → `powops_history` for context.
`powops_verify` proves history hasn't been tampered with.
The agent never writes: no shell, no deploys, no secret access through MCP.

## Architecture

```
powops/
├── powops/                  # Python package
│   ├── __main__.py          # CLI entry point (15 commands)
│   ├── config.py            # Path configuration (STATE_DIR, etc.)
│   ├── garden.py            # SourceStatus + GardenReader (5 check types)
│   ├── health.py            # Cross-garden aggregation + check_all_full()
│   ├── status.py            # CLI table rendering
│   ├── history.py           # Append-only JSONL history + uptime stats
│   ├── volume.py            # Row count tracking + anomaly detection
│   ├── schema.py            # Schema drift detection
│   ├── alerts.py            # State-machine webhook alerting
│   ├── incidents.py         # Durable incident tracking (unique IDs)
│   ├── events.py            # Append-only event stream
│   ├── repos.py             # GitHub commit/CI status
│   ├── backup.py            # R2 sync coordination
│   ├── mcp.py               # MCP server (17 tools)
│   └── sources.yaml         # Universal source manifest
├── web/
│   ├── server.py            # Stdlib HTTP server (port 8796, token/header auth)
│   └── static/
│       ├── index.html       # Dashboard shell
│       ├── app.js           # Dashboard logic
│       └── style.css        # Dashboard styles
├── deploy/
│   └── systemd/
│       ├── powops-dashboard.service   # Dashboard server
│       ├── powops-health.service      # Health snapshot (oneshot)
│       └── powops-health.timer        # Triggers health every 15min
├── tests/
│   ├── test_powops.py       # Core module tests
│   ├── test_new_features.py # History/alerts/volume/schema tests
│   ├── test_mcp.py          # MCP handshake + tool list
│   └── test_mcp_full.py     # All 17 tools over stdio
├── runs/                    # Tested logs (proof of actual runs)
├── reports/
│   ├── AUDIT.md             # (see root AUDIT.md)
│   └── baseline/            # VPS audit, garden status, blockers, peer review
├── vision/                  # Strategy docs (devplan.md is the entry point)
├── threads.md               # Open work items
├── DEVMAP.md                # Development map + priorities
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
├── incidents/               # Incident files (inc-<timestamp>-<garden>-<source>.json)
└── events/                  # Event stream (YYYY-MM-DD.jsonl)
```

### Source Manifest (sources.yaml)

```yaml
gardens:
  my_garden:
    path: /path/to/garden
    description: What this garden collects
    health_check: heartbeat  # or collector_db, raw_mtime, pid_file, pow_health
    storage: warehouse/raw/

sources:
  - id: my_source
    garden: my_garden
    authority: Data Provider
    type: api
    description: What this source provides
    cadence: daily
    health:
      check: heartbeat        # or collector_db (needs source_id), raw_mtime
      file: warehouse/heartbeat.json
      max_staleness: 48h
```

For `pow_health` checks, the garden writes `data/health/<source_id>.json`
using the `pow-health/1` protocol (see powuk/server.py). For
`collector_db`, the `health.source_id` may differ from the powops source
`id` (e.g. powstock `yahoo_finance` reads `yahoo_prices`) — this decoupling
is intentional.

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

70 tests covering:
- Duration and timestamp parsing
- All 5 health check types (heartbeat, collector_db, raw_mtime, pid_file, pow_health)
- False-green rejection (missing/future heartbeats, failed DB runs, live PIDs)
- Health aggregation and overall status
- Status table and JSON rendering
- History recording, querying, timeline dedup, chain verification
- Volume tracking and anomaly detection
- Schema snapshot and drift detection
- Alert state machine (fire-once, suppression, recovery) and webhook payloads
- MCP handshake + all 17 tools over stdio

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
