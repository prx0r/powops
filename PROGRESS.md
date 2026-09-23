# POWOPS Wiring Progress

## Audit Summary

A full connectivity audit identified 39 gaps across severity levels:
- **Critical (5):** Incidents and events modules completely disconnected — write functions never called
- **High (6):** Schema tracking, volume anomaly detection, zero webhook URLs
- **Medium (14):** Missing CLI commands, web endpoints, dashboard tabs, ensure_dirs()
- **Low (14):** Unused imports, dead code, minor inconsistencies

All 69 tests pass before and after changes.

---

## Changes Made

### Critical: Incidents wired into check cycle

**File:** `powops/health.py` — `check_all_full()`

Added incident lifecycle management inside the `if fire_alerts` block:

- **`ok → stale/error/blocked/no_key`**: Calls `create_incident()` and records `incident_opened` event
- **`stale/no_key → error`**: Calls `update_incident()` to escalate severity and records `incident_updated` event
- **`stale/error/blocked/no_key → ok`**: Calls `resolve_incident()` and records `incident_closed` event

Uses `find_open_incident()` to locate existing incidents before updating/resolving.

### Critical: Events wired into check cycle

**File:** `powops/health.py` — `check_all_full()`

Events are now recorded for every state transition:

- Alert fires → `source_stale`, `source_error`, etc. events
- Recovery → `source_recovered` event
- Incident lifecycle → `incident_opened`, `incident_updated`, `incident_closed` events
- Schema drift → `schema_changed` event
- Volume anomaly → `volume_anomaly` event

### High: Schema tracking wired into check_all_full()

**File:** `powops/health.py` — `check_all_full()`

After alerts/incidents processing, iterates results looking for sources with `details.schema` and calls `check_and_update_schema()`. Drift results are added to `actions["schema_drifts"]` and trigger `schema_changed` events.

### High: Volume anomaly detection wired into check_all_full()

**File:** `powops/health.py` — `check_all_full()`

After schema detection, iterates results with records and calls `detect_volume_anomaly()`. Anomalies are added to `actions["volume_anomalies"]` and trigger `volume_anomaly` events.

### Medium: 7 new MCP tools added

**File:** `powops/mcp.py`

| Tool | Description |
|------|-------------|
| `powops_alerts` | Current alert state for all sources |
| `powops_volume` | Volume summary with row count statistics |
| `powops_volume_source` | Volume history for a specific source |
| `powops_timeline` | Status transition timeline for a source |
| `powops_schema` | Latest schema snapshot for a source |
| `powops_schema_history` | Schema change history for a source |

Also fixed imports: removed unused `Tool`, `TextContent`, `STATE_DIR`; added `get_volume_history`, `get_schema_history`, `get_events`.

### Medium: 2 new CLI commands

**File:** `powops/__main__.py`

- **`powops incidents`** — Show incidents with `--status`, `--garden`, `--source`, `--json` filters
- **`powops events`** — Show events with `--days`, `--garden`, `--source`, `--type`, `--json` filters

### Medium: 2 new web API endpoints

**File:** `web/server.py`

- **`GET /api/incidents`** — Query incidents with `?status=`, `?garden=`, `?source=` filters
- **`GET /api/events`** — Query events with `?days=`, `?garden=`, `?source=`, `?type=` filters

### Medium: ensure_dirs() wired into startup

**File:** `powops/__main__.py`

`ensure_dirs()` called at top of `main()` so state directories are created on first run.

### Medium: backup.py reads config, records events

**File:** `powops/backup.py`

- Replaced hardcoded garden paths with `_load_garden_paths()` that reads from `sources.yaml`
- `run_backup()` now calls `record_event()` for `backup_verified` and `backup_failed` events on every sync result

### Medium: 3 new dashboard tabs

**File:** `web/static/index.html`

Added **alerts**, **incidents**, and **events** tabs to the rail navigation with full render functions:
- Alerts tab: shows source, status, last updated
- Incidents tab: shows ID, source, garden, severity, status, opened time
- Events tab: shows time, type, source, garden, severity (last 24h, up to 100 entries)

### Low: Unused imports cleaned up

| File | Removed |
|------|---------|
| `mcp.py` | `Tool`, `TextContent` from mcp.types |
| `health.py` | `_parse_duration`, `_age_since`, `_parse_ts` from garden |
| `schema.py` | `SourceStatus` from garden |
| `events.py` | `__import__('datetime')` hack replaced with proper `timedelta` import |

---

## Remaining Items

### Not yet addressed

| Item | Severity | Notes |
|------|----------|-------|
| `SourceStatus.bytes_new` never assigned | Low | Field exists but no reader populates it |
| `bytes_new` not in `to_verified_dict()` | Low | Dependent on above |
| `render_json()` imported but never called in CLI | Low | Dead code |
| `http` check type referenced in YAML but not implemented | Low | Comment says "(future)" |
| Zero sources have working webhook URLs | High | Configurable — needs real webhook URLs in sources.yaml |
| `alerting.default_webhook` is null | High | Needs a real URL or the feature is a no-op |
| No `incidents` or `events` MCP tools that write | Medium | Read-only MCP tools; creation happens in check cycle |

### Architecture notes

The incidents and events write paths are intentionally coupled to `check_all_full()`. This means:
- Incidents open/close when `powops full` runs (every 15min via systemd timer)
- Events are only created during full check cycles, not on individual `powops check` calls
- MCP tools are read-only for incidents/events — the agent can query but not create
- Web endpoints are read-only — no POST routes exist yet

If you want the agent to create incidents directly, add a `powops_create_incident` MCP tool.
If you want the dashboard to create events, add POST routes to the web server.

---

## Ministar Work (2026-09-23)

### Three new gardens added to sources.yaml

Added **powproducts**, **powrobots**, and **powphysical** to the source manifest:

| Garden | Sources | Health Check | Status |
|--------|---------|-------------|--------|
| powproducts | 8 sources (robotshop_uk, pci_ids, oshwa, robotis_dynamixel, robot_descriptions, mujoco_menagerie, blender_open_data, microbt_official) | collector_db | 1 ready, 7 not_installed |
| powrobots | 15 sources (hmrc_traders, hmrc_trade, ukri_gtr, rbtx, opss_safety, bara_directory, bgs_minerals, contracts_finder, ons_ppi, find_apprenticeship, companies_house, mouser, farnell, lcsc, ebay_uk) | collector_db | 10 need no auth, 5 need API keys |
| powphysical | 3 sources (lcsc_physical, m5stack, waveshare) | raw_mtime | All fixture-only, no real data |

Total sources now: **46** (up from 29).

### GitHub repo status module

New module: `powops/repos.py`

- Checks latest commit SHA, message, author, date for all 9 POW repos via `gh` CLI
- Checks CI status (check-runs API with fallback to combined status)
- CLI: `powops repos` and `powops repos --json`
- Web: `GET /api/repos`
- Dashboard: "repos" tab showing commit, CI status, date for all repos

### Dashboard mission control tab

Added "repos" tab to the dashboard rail showing:
- Repo name, last commit SHA, commit message, CI status (color-coded), date
- Requires authenticated `gh` CLI on the server

### VPS reality check

```
Overall: PARTIAL OUTAGE

Collecting OK: 13/46 sources
  powpowpow: 7/7 ok (all collectors running)
  repair: 6/7 ok, 1 stale (ebay_uk)

Not collecting: 33/46 sources
  powuk: 0/8 unknown (no health artifacts on disk)
  powstock: 0/7 unknown (no health artifacts on disk)
  powproducts: 0/8 (1 unknown, 7 not_installed)
  powrobots: 0/15 (10 unknown, 5 no_key — need API keys)
  powphysical: 0/3 unknown (no raw data, fixture-only adapters)
```

**Key finding:** 29 of 46 configured sources have no health artifacts on disk. The sources.yaml declares monitoring targets, not proof of collection. Only powpowpow and repair are actually collecting data.

---

## Roadmap Work (2026-09-23)

### P0: Baseline audit — completed

Created `reports/baseline/vps-audit.md` with full inventory:

- 9 repos inventoried with commit SHAs, dates, test counts, CI status
- VPS runtime state verified: systemd services, timers, databases, raw files
- Security findings documented: token exposure, 408 .eml files, CSP issue
- Collection reality: only powpowpow (807K files) and repair (4 files) have real data
- 6 powpowpow services failing, powops-health.service also failing

### P1: Health correctness — completed

Fixed 3 false-green defects in `powops/garden.py`:

1. **Heartbeat**: Now rejects missing, empty, or future-dated `heartbeat_at` timestamps (returns `error` instead of `ok`)
2. **PID file**: Live process without data validation now returns `unknown` (was `ok`)
3. **collector_db**: Failed attempts no longer populate `last_success` — only validated successes do

Added `evidence_level` field to `SourceStatus`:
- `"strong"` for heartbeat and collector_db (data-validated)
- `"weak"` for raw_mtime and pid_file (no data validation)

Updated test `test_live_pid` to expect `unknown` instead of `ok`.

### P4: Durable incidents — completed

Fixed filename/glob mismatch in `powops/incidents.py`:
- Incident IDs now use `-` separator (`inc-20260923-powuk-source`) instead of `:` (`inc:20260923:powuk:source`)
- Glob pattern `inc-*.json` now matches created filenames

### Security — completed

1. **Dashboard token rotated** — new token generated at `~/.powops/dashboard_token`
2. **408 .eml files audited** — all are newsletters/articles about AI agents and security. No actual credentials, PII, or secrets found. Regex matches were false positives (prose discussing security topics).
3. **CSP fixed** — changed from `default-src 'self'` to include `'unsafe-inline'` for script and style sources (dashboard uses inline JS/CSS behind token gate)

### Remaining phases

| Phase | Status | Scope |
|-------|--------|-------|
| P2: Garden discovery | pending | Manifest adapters so gardens own their source defs |
| P3: Collection receipts | pending | Collector-run records with actual ingestion metrics |
| P5: Development integration | pending | GitHub CI/deployment visible in dashboard |
| P6: Mission-control dashboard | pending | Overview, gardens, development views |
| P7: MCP expansion | pending | powops_overview, powops_diagnose, structured reporting |
| P8: Production validation | pending | End-to-end tests, recovery exercises |
