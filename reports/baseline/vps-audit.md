# POWOps Baseline Audit — 2026-09-23

## VPS State Summary

| Repo | Branch | Commit | Date | Tests | CI | Systemd | Raw Files |
|------|--------|--------|------|-------|----|---------|-----------|
| powops | main | cf4bc0e | 2026-09-22 | 5 files | 0 | 3 units | n/a |
| powpowpow | master | f707e9c | 2026-09-21 | 2 files | 0 | 10 units | 807,932 |
| powuk | main | fa77e48 | 2026-09-21 | 5 files | 0 | 0 | 0 |
| powstock | main | c250d43 | 2026-09-21 | 10 files | 0 | 0 | 0 |
| repair | main | d9a5839 | 2026-09-21 | 2 files | 0 | 0 | 4 |
| powproducts | main | e29189d | 2026-09-22 | 3 files | 1 | 0 | 0 |
| powrobots | main | 3a481e3 | 2026-09-21 | 3 files | 0 | 0 | 0 |
| powphysical | main | 93bcdec | 2026-09-22 | 6 files | 0 | 0 | 0 |
| powk | main | 8ee8a43 | 2026-09-21 | 3 files | 0 | 0 | n/a |

## Collection Status

```
Overall: PARTIAL OUTAGE

Actually collecting: 13/55 sources
  powpowpow: 7/7 ok (807K raw files, real data)
  repair: 6/7 ok, 1 stale (4 raw files only)

Not collecting: 42/55 sources
  powuk: 0/8 unknown (0 raw files, no health artifacts)
  powstock: 0/7 unknown (0 raw files, no health artifacts)
  powproducts: 0/8 (1 unknown, 7 not_installed, 0 raw files)
  powrobots: 0/15 (10 unknown, 5 no_key, 0 raw files)
  powphysical: 0/3 unknown (0 raw files, fixture-only adapters)
```

## Systemd Services

Running:
- pow-chain-state.service (powpowpow chain poller)
- pow-pearld.service (Pearl node)
- pow-site.service (consumer site)
- pow-venue-l2.service (venue L2 archival)
- pow-venue-ws.service (venue WS tick archiver)
- pow-tunnel.service (cloudflared tunnel)
- powops-dashboard.service (dashboard)
- powops-tunnel.service (powops tunnel)

Failed:
- pow-daily-state.service (daily rollup)
- pow-qubic-computors.service (qubic snapshots)
- pow-qubic-epoch.service (qubic epoch engine)
- pow-seed-rebuild.service (seed rebuild)
- pow-tardis-reload.service (tardis reload)
- pow-tardis-remainder.service (tardis remainder)
- powops-health.service (health snapshot)

Timers:
- powops-health.timer: fires every 15min (last run: 7min ago) — working
- pow-qubic-epoch.timer: fires every 5min — service failing
- pow-qubic-computors.timer: fires hourly — service failing
- pow-daily-state.timer: fires daily — service failing

## Databases

| Database | Exists | Tables | Notes |
|----------|--------|--------|-------|
| repair/warehouse/repair.db | yes | (empty) | No tables found |
| powproducts/warehouse/powproducts.db | yes | (empty) | Schema v2 but no data |
| powrobots/warehouse/powrobots.db | no | n/a | Warehouse dir exists, no DB |

## Security Findings

1. **CRITICAL: Dashboard token exposed** — PEER_REVIEW.md documents prior token exposure. Token still present in dashboard_token file. Must verify rotation.
2. **408 .eml files in powpowpow** — committed in commit 4df9c94. Need audit for PII/credentials.
3. **CSP too restrictive** — `default-src 'self'` blocks inline JS/CSS used by dashboard. Either fix CSP or move to separate assets.
4. **No GitHub Actions on 8/9 repos** — only powproducts has a workflow. CI coverage is zero for most repos.
5. **5 sources need API keys** — powrobots: companies_house, mouser, farnell, lcsc, ebay_uk.

## Key Observations

- Only powpowpow has real data (807K files). Repair has 4 files. All other gardens have zero.
- The powops-health.timer is firing but the health service is failing — need to investigate why.
- 6 powpowpow services are failing — these are collector failures, not powops failures.
- powproducts DB has schema v2 but no tables — the DB was created empty.
- powrobots has no database at all despite the warehouse directory existing.

## Baseline States

| State | Gardens |
|-------|---------|
| Documented | all 9 |
| Implemented | powpowpow, repair (collectors exist) |
| Tested | powpowpow, repair (tests pass) |
| Deployed | powpowpow (systemd services running) |
| Collecting | powpowpow (7 sources), repair (6 sources) |
| Historically backfilled | powpowpow (807K files) |
