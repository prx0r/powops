# Open Threads — 2026-09-23

Everything that's unfinished, broken, blocked or waiting on something.

---

## Thread 1: powuk broken collectors

**Status:** 4 collectors failing
**Impact:** 4 sources stuck at error

| Collector | Error | Fix needed |
|-----------|-------|-----------|
| ons_skills | ONS URL returns 404 | Find current dataset URL from ONS |
| ons_salaries | ONS URL returns 404 | Find current dataset URL from ONS |
| find_tender | API returns 400 "Request parameters unknown" | API changed, update endpoint in server.py |
| evspark_trades | Permission denied on /root/ab/ path | Hardcoded path in collector, needs config |

**Next:** Search ONS for current dataset URLs. The old URLs in server.py are stale.

---

## Thread 2: powstock not visible to powops

**Status:** Collectors run successfully but powops shows 0/18
**Impact:** powstock data exists but isn't monitored

**Problem:** powstock health artifacts exist in `data/health/` but powops uses `collector_db` check type for powstock sources. powstock doesn't have a `collector_run` table that powops can query.

**Fix options:**
1. Change powstock sources in sources.yaml to use `pow_health` check type
2. Or add `collector_run` table to powstock DB

---

## Thread 3: powproducts robotshop_uk collector bugs

**Status:** Collector runs but has attribute errors
**Impact:** 0/8 powproducts sources working

**Errors:**
- `'RobotShopCollector' object has no attribute 'requests_attempted'`
- Collector returns `CollectorResult` object without `.status` attribute

**Fix:** The robotshop collector needs updating to match the base collector interface.

---

## Thread 4: powphysical has no real adapters

**Status:** 3 fixture-only stubs
**Impact:** 0/3 powphysical sources working

**What exists:** lcsc, m5stack, waveshare adapters that return hardcoded data
**What's needed:** Real API integrations (LCSC has a documented API)

---

## Thread 5: powproducts health artifacts missing

**Status:** No health artifacts written
**Impact:** powops can't see powproducts collection state

**Fix:** Add health artifact writing to powproducts collector runner (same pattern as powuk/powstock).

---

## Thread 6: repair remaining collectors not run

**Status:** Only open_repair has been run
**Impact:** 6/7 repair sources not collecting

**Not run:** dvla, land_registry, planning_data, eprel, france_repairability, ebay_uk

**ebay_uk is blocked** — needs API key or different approach.

---

## Thread 7: powrobots needs API keys

**Status:** 5 sources blocked on missing keys
**Impact:** 5/15 powrobots sources not collecting

| Source | Key needed |
|--------|-----------|
| companies_house | COMPANIES_HOUSE_API_KEY |
| mouser | MOUSER_API_KEY |
| farnell | FARNELL_API_KEY |
| lcsc | LCSC_API_KEY |
| ebay_uk | EBAY_APP_ID |

**Note:** CH key exists in powuk/.env but powrobots doesn't read it.

---

## Thread 8: powops sources.yaml has wrong paths

**Status:** Fixed for powuk and powstock, but may have other issues
**Impact:** Health checks fail if paths are wrong

**Fixed:**
- powuk: `/root/powuk` → `/home/ubuntu/powuk`
- powstock: `/root/powstock` → `/home/ubuntu/powstock`

**Verify:** All garden paths in sources.yaml match actual VPS paths.

---

## Thread 9: dashboard security

**Status:** Token was rotated but CSP is weakened
**Impact:** Security posture

**Done:**
- Dashboard token rotated
- PEER_REVIEW.md documented prior exposure

**Open:**
- CSP uses `'unsafe-inline'` for scripts/styles
- URL query token auth (should move to headers)
- No Cloudflare Access in front of dashboard

---

## Thread 10: powops health service failing

**Status:** powops-health.service shows as failed in systemd
**Impact:** Health checks may not be running on schedule

**Check:** `systemctl --user status powops-health.service`

---

## Thread 11: cross-garden dependency gaps

**Status:** powuk is the bottleneck
**Impact:** 4 gardens need powuk data

| Consumer | Needs | Status |
|----------|-------|--------|
| powrobots | ch_capacity | Working (6 rows) |
| powproducts | open_repair | Source doesn't exist in powuk |
| powphysical | ons_salaries | URL broken (404) |
| repair | contracts_finder | Rate limited |

---

## Thread 12: ONS dataset URLs

**Status:** Multiple ONS URLs returning 404
**Impact:** ons_salaries, ons_skills, ons_labour (partially) affected

**Action needed:** Search ONS website for current dataset download URLs. The URLs in server.py were working as of 2025 but ONS reorganizes their file structure periodically.

---

## Thread 13: contracts_finder rate limiting

**Status:** API returns 429 when called frequently
**Impact:** powuk and powrobots contracts_finder collectors fail

**Fix:** Add rate limiting / retry logic, or reduce collection frequency.

---

## Thread 14: powuk has 11 sources with no collectors

**Status:** Manifests exist but no collector implementations
**Impact:** 11/24 powuk sources never collect

**Sources without collectors:** ofqual, nomis_supply, dfe_apprenticeships, refcom, open_repair, epc_stock, legislation, gov_publications, gov_grants, neso_tec, onsalaries

**Note:** Some of these (open_repair, epc_stock) don't exist in powuk's source registry.

---

## Thread 15: vision docs need consolidation

**Status:** 11 docs in vision/ with overlapping content
**Impact:** Confusion about which doc is authoritative

**Recommendation:** devplan.md should be the single source of truth. Others are research/strategy archives.

---

## Thread 16: PROGRESS.md is stale

**Status:** Last updated during wiring session
**Impact:** Doesn't reflect current state

**Update needed:** Add powuk/powstock/repair collection results, blockers, current status.

---

## Thread 17: .gitignore may be missing entries

**Status:** Data files may be getting committed
**Impact:** Repo bloat

**Check:** `.gitignore` should exclude `data/`, `warehouse/`, `*.db`, `__pycache__/`, `.env`

---

## Thread 18: no systemd timer for powstock/powproducts/repair

**Status:** Only powops-health.timer exists
**Impact:** Other gardens don't collect on schedule

**Need:** Systemd timers or cron jobs for each garden's collectors.

---

## Thread 19: powops tests don't cover new modules

**Status:** 69 tests pass but don't test repos.py, incidents.py, events.py in production
**Impact:** New code paths untested

**Add:** Tests for repos.py (mock gh CLI), incident lifecycle, event recording.

---

## Thread 20: MCP server needs expansion

**Status:** 17 tools, but missing powops_diagnose
**Impact:** Agent can query but can't get structured diagnostics

**From roadmap.md:** `powops_diagnose` should compare actual evidence with expectations and produce possible causes.

---

## Priority order

1. **Thread 2** — powstock→powops wiring (quick fix, high impact)
2. **Thread 5** — powproducts health artifacts (quick fix, high impact)
3. **Thread 6** — repair remaining collectors (medium effort, high impact)
4. **Thread 1** — powuk broken URLs (needs research, medium impact)
5. **Thread 3** — powproducts collector bugs (needs code fix, medium impact)
6. **Thread 7** — API keys (needs user input)
7. **Thread 4** — powphysical adapters (large effort, lower priority)
