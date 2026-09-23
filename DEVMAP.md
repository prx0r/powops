# POW Development Map

**Current state:** 31/42 installed sources OK across 7 gardens (82 configured). MCP live. Dashboard live.
**Date:** 2026-09-23

---

## Garden MCP landscape (2026-09-23)

Each garden is growing its own interface. powops is the integrated monitoring layer.

| Garden | Own MCP? | Own API? | Tools | Pi agent access |
|--------|----------|----------|-------|-----------------|
| powops | yes (17 tools) | yes (dashboard) | status, history, uptime, incidents, events, coverage, schemas, verify, sources, alerts, volume, timeline, repos | enabled in opencode.jsonc |
| powstock | yes (11 tools) | yes (FastAPI) | health, universe, prices, insiders, short_interest, rns, companies, signals, runs, collectors, summary | enabled 2026-09-23 (`-m powstock.mcp --stdio`) |
| powpowpow | yes (8 local, 11 upstream) | yes (site/server.py) | asset_state, signals, factors, compute_routes, miner_pressure, brief, price_history, health (+get_live, +get_xmr_full, +get_opportunity upstream) | enabled 2026-09-23 (venv python, FastMCP stdio) |
| powphysical | yes (6 tools) | no | search, resolve, compare, save_build, get_build, reprice | DISABLED — fixture data only |
| powuk | no (spec only) | no (collector runner) | — | via powops only |
| repair | no | no | — | via powops only |
| powproducts | no | no | — | via powops only |
| powrobots | no | no | — | via powops only |
| powk | no | no | — | via powops only |

**Rule:** pi agent talks to gardens through powops for health/monitoring. Direct garden MCPs are for domain data (prices, signals, builds) once enabled. Do not enable powphysical's MCP until adapters return real data.

---

## What exists today

```
┌─────────────────────────────────────────────────────────────────┐
│                        POWOPS                                    │
│                                                                  │
│  CLI: 15 commands                                                 │
│  MCP: 17 tools (live for pi agent)                               │
│  Dashboard: 9 tabs (status, history, uptime, volume, schemas,   │
│             alerts, incidents, events, repos)                    │
│  Tests: 69 passing                                               │
│  Sources: 82 configured, 27 collecting                           │
└─────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │  powpowpow  │ │   repair    │ │    powuk    │
     │  7/7 OK     │ │  1/7 OK     │ │  9/24 OK    │
     │  807K files │ │  13K records│ │  175K rows  │
     └─────────────┘ └─────────────┘ └─────────────┘
            │               │               │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │  powrobots  │ │  powstock   │ │ powproducts │
     │  9/15 OK    │ │  0/18 visible│ │  1/8 OK     │
     │  11 raw files│ │  24 prices  │ │  code bugs  │
     └─────────────┘ └─────────────┘ └─────────────┘
                            │
                     ┌──────▼──────┐
                     │ powphysical │
                     │  0/3 OK     │
                     │  stubs only │
                     └─────────────┘
```

---

## Priority 1: Make what exists actually work (this week)

### 1.1 Wire powstock to powops
**Why:** powstock collectors run and produce data (24 prices, 891 RNS, 422 short interest) but powops shows 0/18 because the collector_run view is empty.
**Fix:** Either fix ingest_run recording in powstock, or switch powstock sources to `pow_health` check type (heartbeat.json exists).
**Effort:** 1 hour
**Impact:** +18 sources visible

### 1.2 Wire events into check_all()
**Why:** powops_events returns 0 because record_event() is only called in check_all_full(), not check_all(). The MCP tool exists but has no data.
**Fix:** Add event recording to check_all() for status transitions.
**Effort:** 30 minutes
**Impact:** Events tab fills up, incidents get event trails

### 1.3 Fix powproducts robotshop_uk collector
**Why:** Collector has code bugs (missing requests_attempted attribute). Infrastructure is fixed but collector can't run.
**Fix:** Update robotshop collector to match base collector interface.
**Effort:** 1 hour
**Impact:** +1 source, first powproducts data

### 1.4 Run repair remaining collectors
**Why:** Only open_repair has been run. 5 more collectors exist (dvla, land_registry, planning_data, eprel, france_repairability).
**Fix:** Run each collector, verify data.
**Effort:** 2 hours
**Impact:** +5 sources, repair garden fills out

---

## Priority 2: Fill the dashboard gaps (this week)

### 2.1 Dashboard "repos" tab needs gh CLI
**Why:** The repos tab shows commit/CI status but requires authenticated gh CLI. Currently shows nothing.
**Fix:** Install gh CLI and authenticate, or use GitHub API with token.
**Effort:** 30 minutes
**Impact:** Development visibility in dashboard

### 2.2 Dashboard "alerts" tab is empty
**Why:** No webhook URLs configured in sources.yaml. The alerting system works but has no destinations.
**Fix:** Add at least one webhook URL (could be a Slack/Discord webhook for testing).
**Effort:** 15 minutes
**Impact:** Alerts tab shows data, alerting becomes functional

### 2.3 Dashboard "schemas" tab is empty
**Why:** No sources provide schema info to health checks. The schema module exists but nothing feeds it.
**Fix:** Add schema extraction to at least one collector (e.g., open_repair CSV columns).
**Effort:** 2 hours
**Impact:** Schema drift detection becomes active

### 2.4 Dashboard "incidents" tab is empty
**Why:** Incidents only get created when check_all_full() runs and detects status changes. Need to run it.
**Fix:** Run `powops full` to trigger incident creation on current stale/error sources.
**Effort:** 5 minutes
**Impact:** Incidents tab shows real problems

---

## Priority 3: Fix broken collectors (next week)

### 3.1 powuk ONS URLs
**Why:** ons_skills and ons_salaries return 404. ONS reorganized their file structure.
**Fix:** Search ONS website for current dataset URLs, update server.py.
**Effort:** 1 hour research
**Impact:** +2 sources

### 3.2 powuk find_tender API
**Why:** API returns 400 "Request parameters unknown". Endpoint changed.
**Fix:** Find current Find a Tender API endpoint.
**Effort:** 1 hour research
**Impact:** +1 source

### 3.3 powuk contracts_finder rate limiting
**Why:** API returns 429 when called frequently.
**Fix:** Add rate limiting / retry logic, reduce collection frequency.
**Effort:** 30 minutes
**Impact:** +1 source stable

---

## Priority 4: Fill remaining gardens (next 2 weeks)

### 4.1 powrobots API keys
**Why:** 5 sources blocked on missing keys (companies_house, mouser, farnell, lcsc, ebay_uk).
**Fix:** User needs to provide API keys.
**Effort:** User action
**Impact:** +5 sources

### 4.2 powproducts remaining collectors
**Why:** 7 sources marked not_installed. Collectors exist but haven't been implemented.
**Fix:** Implement pci_ids, oshwa, robotis_dynamixel, robot_descriptions, mujoco_menagerie, blender_open_data, microbt_official.
**Effort:** 1-2 days
**Impact:** +7 sources

### 4.3 powphysical real adapters
**Why:** 3 fixture-only stubs (lcsc, m5stack, waveshare). No real data.
**Fix:** Implement real LCSC adapter (API exists), others as scrapers.
**Effort:** 2-3 days
**Impact:** +3 sources, first supplier data

### 4.4 powuk remaining collectors
**Why:** 11 sources with manifests but no collectors (ofqual, refcom, epc_stock, legislation, etc.).
**Fix:** Implement collectors for each.
**Effort:** 3-5 days
**Impact:** +11 sources

---

## Priority 5: Cross-garden data flow (week 3)

### 5.1 powrobots → powuk data dependency
**Why:** powrobots needs ch_capacity from powuk for UK business data. ch_capacity works (6 rows) but powrobots doesn't consume it yet.
**Fix:** Build cross-garden data import in powrobots.
**Effort:** 2 days
**Impact:** powrobots gets UK business context

### 5.2 repair → powuk data dependency
**Why:** repair needs contracts_finder and open_repair from powuk. contracts_finder is rate-limited, open_repair doesn't exist in powuk.
**Fix:** Add open_repair source to powuk, fix rate limiting.
**Effort:** 1 day
**Impact:** repair gets demand signals

### 5.3 powproducts → repair data dependency
**Why:** powproducts needs open_repair from repair for demand signals.
**Fix:** Build cross-garden data import.
**Effort:** 1 day
**Impact:** powproducts knows what's breaking

### 5.4 powphysical → powuk data dependency
**Why:** powphysical needs ons_salaries for regional cost intelligence. URL is broken.
**Fix:** Fix ONS URL, build import.
**Effort:** 1 day
**Impact:** powphysical gets cost data

---

## Priority 6: Transaction layer (month 2)

### 6.1 Spare parts first transaction
**Why:** The goldmoat thesis says spare parts are the first transaction layer. Need to prove someone will pay.
**Fix:** Select 10 SKUs, get quotes, list on a simple storefront, measure demand.
**Effort:** 1 week
**Impact:** First revenue, outcome data

### 6.2 BOM-to-purchase for SO-101
**Why:** The roadmap says SO-101 is the first reference design. Need complete BOM with UK-delivered quote.
**Fix:** Get SO-101 BOM into powproducts, resolve parts, generate quote.
**Effort:** 3 days
**Impact:** First kit product

### 6.3 MCP procurement tools
**Why:** The goldmoat2.md says expose procurement through MCP for AI assistants.
**Fix:** Add powops_resolve_bom, powops_find_substitutes, powops_quote_build tools.
**Effort:** 1 week
**Impact:** AI agents can source parts

---

## Priority 7: Consumer products (month 3)

### 7.1 POW Agent Node prototype
**Why:** robotprintify.md says ESP32 plant agent is the first consumer product.
**Fix:** Design board, order components, build 5 prototypes.
**Effort:** 2 weeks
**Impact:** First consumer product

### 7.2 Etsy listing
**Why:** robotprintify.md says Etsy is the proving ground.
**Fix:** List plant agent on Etsy with personalisation options.
**Effort:** 1 week
**Impact:** First consumer sales, outcome data

---

## Dashboard wiring status

| Tab | Data source | Has data? | Wired? |
|-----|-------------|-----------|--------|
| status | /api/status | YES (82 sources) | YES |
| history | /api/history | YES (165+ entries) | YES |
| uptime | /api/uptime | YES (65 sources) | YES |
| volume | /api/volume | YES (17 sources) | YES |
| schemas | /api/schemas | NO (0 schemas) | YES but empty — no sources emit schema info |
| alerts | /api/alerts | NO (0 alerts) | YES but empty — no webhook URLs configured |
| incidents | /api/incidents | fills on `powops full` | YES — run full to populate |
| events | /api/events | YES (flows on status change) | YES — wired into check_all() 2026-09-23 |
| repos | /api/repos | needs gh CLI auth | YES but blocked on auth |

**Dashboard is fully wired.** All 9 tabs connect to real API endpoints. The gaps are in data, not code. powstock visibility fixed 2026-09-23 (switched to pow_health check type + source_id mapping + dispatch fix).

---

## The path to 82/82

```
TODAY:      27/82 (33%)
Week 1:     45/82 (55%)  — fix powstock, events, robotshop, repair collectors
Week 2:     60/82 (73%)  — fix ONS URLs, find_tender, add API keys
Week 3:     75/82 (91%)  — implement remaining collectors, cross-garden deps
Month 2:    82/82 (100%) — all sources collecting
Month 3:    first transaction, first consumer product
```

---

## What the pi agent can do RIGHT NOW

```bash
# Query any source health
powops_status                    # all 82 sources
powops_source chain_state        # one source

# Get history
powops_history --days 7          # last week
powops_uptime --days 30          # monthly uptime

# Monitor problems
powops_incidents                 # open incidents
powops_events --days 1           # recent events
powops_alerts                    # alert state

# Verify integrity
powops_verify --days 7           # chain hash check

# Check specific gardens
powops_status --garden powuk     # just powuk
powops_status --garden repair    # just repair
```

---

## What the pi agent CAN'T do yet

1. Run collectors (read-only MCP)
2. Fix broken sources
3. Add new sources to sources.yaml
4. Access raw data from gardens directly
5. Query garden-specific databases
6. Trigger alerts or incidents
7. Manage API keys
8. Deploy code changes

**These are all intentional.** The pi agent monitors and reports. Humans or coding agents make changes.
