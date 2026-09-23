# Peer Review — powops, 2026-09-23

Method: live code reading + behavioral probes against the running system.
Every claim below was reproduced, not inferred.

## Critical (fixed this session)

### 1. Event spam from read path — FIXED
`check_all()` recorded transition events on every call but never advanced
alert state. Dashboard (/api/uptime calls check_all), MCP and CLI status
all triggered it. Evidence: 34x duplicate `source_recovered/open_repair`
in one day's event stream.
Fix: events only in `check_all_full`, which owns the state lifecycle.
Verified: 2x check_all + 1x dry-run full → 0 new events (83→83).

### 2. Incidents could never fire correctly, then fired duplicates — FIXED
Two compounding defects in `check_all_full`:
(a) incident comparison read alert state AFTER `process_alerts` saved the
new state → old==new always → incidents never opened (dead code in practice).
Fixed earlier by snapshotting pre-state.
(b) open branch had no idempotency guard and defaulted missing entries to
"ok" → first sighting of any unconfigured problem source opened an
incident on EVERY run (8x incident_opened/companies_house, 5x ebay_uk).
Fix: default "unknown" (observe, don't open), skip open when one is open,
skip all incident writes on dry_run.
Verified: forced ok→stale transition opens exactly one incident.

### 3. Dead health timer — FIXED
`powops-health.service` failed every 15min since deployment (exit 209:
`StandardOutput=append:/var/log/...` unwritable by user service).
No history/incidents/events were recording on schedule. Removed the lines
(journal captures output). Service green, history growing 575→903 entries.

### 4. powstock audit blackout — FIXED (powstock repo)
`IngestRun.start()` omitted `retrieved_at` (NOT NULL) → every collector
run crashed at INSERT. Data tables populated by older code; zero run
records. One-line fix, pushed upstream.

## High (open)

### 5. Same-day incident IDs collide (thread 26)
IDs are `inc-YYYYMMDD-garden-source`. A second intraday outage overwrites
the first file. Verified live. Needs unique IDs + migration (roadmap P4).

### 6. Source IDs not namespaced (roadmap 4.2)
`ebay_uk` exists in repair AND powrobots. Incident lookup is by source_id
only — cross-garden collisions possible. Verified: test incident attached
to the wrong garden's source.

### 7. Repair manifest drift (thread 24)
powops monitors 7 legacy repair IDs; repair's daemon runs 7 different
ones. Only open_repair overlaps. 6/7 repair sources can never go green
without P2 reconciliation.

### 8. No webhook URLs configured
Alerting state machine works (verified fire-once/suppress/recovery), but
0 webhooks exist. Alerts tab shows state, nothing notifies anyone.

## Medium (open)

### 9. Dashboard token in URL query
Works (401s verified) but tokens leak into logs/history. Roadmap 10.1
(Cloudflare Access + header auth) not started.

### 10. CSP uses unsafe-inline
Required by current single-file SPA. Documented; needs asset split.

### 11. ONS collectors dead (ons_skills, ons_salaries 404; find_tender 400)
Upstream changed. Low ROI to chase; documented in threads.md.

### 12. 5 powrobots sources need API keys
companies_house, mouser, farnell, lcsc, ebay_uk. Needs human.

## Low (fixed this session unless noted)

- File-handle leak in `list_history_files` — FIXED (context manager).
- Dead `render_json` import in CLI — FIXED (removed).
- `status_icon` no-op dict (returns input unchanged) — OPEN, cosmetic.
- `readers["_config"]` manifest smuggling in health.py — OPEN, structural.
- `SourceStatus.bytes_new` never assigned, absent from output — OPEN, harmless.
- MCP payloads >64KB/line (status, sources) — client-side readline limits
  truncate; opencode handles it. Noted for external consumers.
- test_mcp.py DeprecationWarning (get_event_loop) — OPEN, cosmetic.

## Performance (measured)
check_all 82 sources: 0.12s. Endpoints: status 0.10s, history 0.01s,
uptime 0.36s (slowest, runs live check_all), volume 0.04s, repos 2.7s
(subprocess, unauthenticated). No perf action needed.
