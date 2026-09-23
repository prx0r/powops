# HANDOVER — powops, 2026-09-23

> Read this first. Then AGENTS.md for operations, threads.md for open work.

## Current state

- **31/42 installed sources OK** (88 configured, rest not_installed/unknown). Overall: degraded (honest — partial outage is real).
- **70/70 tests pass**, zero warnings.
- **Dashboard live** at 127.0.0.1:8796 (systemd). 9 tabs, all wired, all endpoints 200.
- **MCP live**: 17 tools, enabled in opencode.jsonc. Full stdio suite passes.
- **Health timer fixed**: was dead (exit 209 every 15min), now green. History/incidents/events record on schedule.
- **Latest commit**: check `git log --oneline -3`.

## What just happened (Sept 22–23)

1. Wired incidents/events/schema/volume-anomaly into the check cycle.
2. Fixed 4 critical defects: event spam from reads, incident duplicates, dead timer, powstock audit blackout.
3. Fixed 8 peer-review flaws: unique incident IDs, garden-scoped lookup, Bearer auth, CSP asset split, _config refactor, dead code removal, asyncio warnings, repair daemon sources added.
4. Added 7 gardens to monitoring (was 4), 88 sources (was 29).
5. Wrote vision docs (vision/devplan.md is the entry point), audit docs, tested logs in runs/.

## What's running right now

```bash
systemctl --user status powops-dashboard.service powops-health.timer
# dashboard: active (serves UI + API)
# timer: fires `powops full` every 15min (records history/incidents/events)
```

## Open work (see threads.md, newest first)

- Thread 28: powrobots goldmoat progress tracked, first paid order pending.
- Thread 27: needs human — webhook URL, 5 API keys, ONS URLs, Cloudflare Access, ID namespacing migration.
- Thread 26: same-day incident IDs — FIXED (microsecond stamps).
- Thread 24: repair manifest drift — partially fixed (daemon IDs added, 4 OK).
- Thread 21: powpowpow pull blocked by local backtest rewrite — needs owner merge.

## Where things are

| Need | File |
|------|------|
| Operate this repo | AGENTS.md |
| Repo map + interface matrix | AUDIT.md |
| Open work | threads.md |
| Priorities + coverage path | DEVMAP.md |
| What every repo builds toward | vision/devplan.md |
| Known flaws | reports/peer-review-2026-09-23.md |
| Proof logs | runs/ (timestamped) |
| Baseline inventory | reports/baseline/ |

## The one rule

**Reads never write.** `check_all()` is called by dashboard/MCP/CLI on every
view — no events, no state saves, no incidents there. All writes live in
`check_all_full()`. Breaking this caused the worst bugs to date.

## For the next agent

1. Run `python3 -m powops status` and `python3 -m pytest tests/` first.
2. Read threads.md newest-first before starting anything.
3. Small PRs, test after every change, commit + push when green.
4. Never store credentials in git config — check `git remote -v` is clean.
5. Don't pull powpowpow blindly (local work + upstream divergence, thread 21).
