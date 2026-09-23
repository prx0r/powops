# AGENTS.md — powops operations

> Layer 1 command centre for POW gardens. Answers one question: is the data flowing?

## What this is

powops monitors every data source across 7 POW gardens (powpowpow, repair,
powuk, powstock, powproducts, powrobots, powphysical). It does not model,
does not trade, does not collect domain data itself. It reads health
artifacts from each garden and reports collection status.

Three interfaces share one backend (`powops/health.py`):
- **CLI** — `python3 -m powops <command>` (15 commands, see README.md)
- **Dashboard** — stdlib HTTP on 127.0.0.1:8796 (9 tabs, token or Bearer auth)
- **MCP** — `python3 -m powops.mcp` (17 read-only tools for the pi agent)

## The one rule

**Reads must not write.** `check_all()` is called by the dashboard, MCP and
CLI on every view. It must never record events, touch alert state, or create
incidents. All writes happen in `check_all_full()` (timer-driven), which owns
the alert-state lifecycle. Violating this caused duplicate events/incidents
in the past — see reports/peer-review-2026-09-23.md.

## How to operate

```bash
cd /home/ubuntu/powops
python3 -m powops status              # live table
python3 -m powops full --dry-run      # full cycle, no alert writes
python3 -m pytest tests/              # 70 tests, must all pass
systemctl --user status powops-dashboard.service powops-health.timer
journalctl --user -u powops-health.service -n 20   # timer output
```

## Health check types (in garden.py)

| check | evidence | rule |
|-------|----------|------|
| heartbeat | strong | reject missing/future `heartbeat_at` |
| collector_db | strong | failed runs never count as success |
| pow_health | strong | garden writes `data/health/<id>.json` (pow-health/1) |
| raw_mtime | weak | file times only, never proof of collection |
| pid_file | weak | live PID without data = `unknown`, never `ok` |

`health.source_id` may differ from the powops source `id` (e.g. powstock
`yahoo_finance` reads artifact `yahoo_prices`). This decoupling is intentional.

## State locations

- Runtime state: `~/.powops/` (history, volume, schemas, alerts.json, incidents, events)
- Garden data: stays in each garden's repo. powops never writes there.
- Dashboard token: `~/.powops/dashboard_token`. Rotate by replacing the file
  and restarting the dashboard service.

## What belongs here vs gardens

**powops owns:** source registry (sources.yaml), health aggregation, history,
alerts, incidents, events, dashboard, MCP, timers.
**Gardens own:** collectors, raw data, databases, their own health artifacts.
If a garden changes collector IDs, update sources.yaml — do not copy garden
logic into powops. Cross-repo manifest discovery is roadmap P2 (not built).

## Key files for agents

| File | Why |
|------|-----|
| AUDIT.md | full repo map + interface consistency matrix |
| threads.md | open work, newest first (thread 21+) |
| DEVMAP.md | priorities + path to full coverage |
| vision/devplan.md | what every repo is building toward |
| reports/peer-review-2026-09-23.md | known flaws, fixed vs open |
| runs/ | timestamped proof logs (pytest, status, MCP, dashboard) |

## Git

```bash
cd /home/ubuntu/powops
git add -A && git commit -m "description" && git push origin main
```

Remote: `https://github.com/prx0r/powops`. No credentials on this VPS —
pushes need a token supplied at push time; never store one in remote config
(check `git remote -v` shows no embedded credentials).
