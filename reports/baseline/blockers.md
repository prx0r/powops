# Blockers — 2026-09-23

## What's working (26/37 sources OK)

| Garden | OK | Total | Status |
|--------|-----|-------|--------|
| powpowpow | 7 | 7 | All collectors running |
| repair | 1 | 7 | open_repair working (13K records), 5 others not run |
| powuk | 9 | 24 | 9 collectors working, 4 broken URLs, 11 not implemented |
| powrobots | 9 | 15 | 10 sources collecting, 5 need API keys |
| powstock | 0 | 18 | Collectors run but health artifacts not wired to powops |
| powproducts | 0 | 8 | Infrastructure exists, never run |
| powphysical | 0 | 3 | Fixture-only stubs, no real data |

---

## Blockers by garden

### powuk (9/24)

| Source | Issue | Fix |
|--------|-------|-----|
| ons_skills | ONS URL returns 404 | Find current ONS dataset URL |
| ons_salaries | ONS URL returns 404 | Find current ONS dataset URL |
| find_tender | API returns 400 "Request parameters unknown" | API changed, need to update endpoint |
| evspark_trades | Permission denied on /root/ab/ path | Hardcoded path, needs config |
| ofqual | No health artifact (collector not in server.py) | Implement collector |
| nomis_supply | No health artifact | Implement collector |
| dfe_apprenticeships | No health artifact | Implement collector |
| refcom | No health artifact | Implement collector |
| open_repair | Source doesn't exist in powuk | Add to sources.yaml |
| epc_stock | No health artifact | Implement collector |
| legislation | No health artifact | Implement collector |
| gov_publications | No health artifact | Implement collector |
| gov_grants | No health artifact | Implement collector |
| contracts_finder | Health artifact shows 0 rows (API rate limited) | Re-run when rate limit clears |

### repair (1/7)

| Source | Issue | Fix |
|--------|-------|-----|
| ebay_uk | Collector blocked | Needs API key or different approach |
| dvla | Not run | Run collector |
| land_registry | Not run | Run collector |
| planning_data | Not run | Run collector |
| eprel | Not run | Run collector |
| france_repairability | Not run | Run collector |

### powstock (0/18 visible to powops)

| Source | Issue | Fix |
|--------|-------|-----|
| yahoo_prices | RHL.L delisted (404) | Remove from universe |
| companies_house | Needs API key | Use same key as powuk |
| All others | Health artifacts exist but powops can't read them | powstock uses different check type |

### powproducts (0/8)

| Source | Issue | Fix |
|--------|-------|-----|
| robotshop_uk | Never run | Run first collector |
| All others | Marked not_installed | Implement collectors |

### powphysical (0/3)

| Source | Issue | Fix |
|--------|-------|-----|
| lcsc | Fixture-only adapter | Implement real LCSC adapter |
| m5stack | Fixture-only adapter | Implement real adapter |
| waveshare | Fixture-only adapter | Implement real adapter |

---

## Cross-garden dependencies (from devplan.md)

| Consumer | Needs | Status |
|----------|-------|--------|
| powrobots | powuk/ch_capacity | Working (6 rows) |
| powproducts | powuk/open_repair | Source doesn't exist in powuk |
| powphysical | powuk/ons_salaries | URL broken (404) |
| repair | powuk/contracts_finder | Rate limited, 0 rows |
| repair | powuk/open_repair | Source doesn't exist in powuk |

---

## API keys needed

| Source | Key | Status |
|--------|-----|--------|
| companies_house | COMPANIES_HOUSE_API_KEY | Configured in powuk/.env |
| powrobots: companies_house | COMPANIES_HOUSE_API_KEY | Not set |
| powrobots: mouser | MOUSER_API_KEY | Not set |
| powrobots: farnell | FARNELL_API_KEY | Not set |
| powrobots: lcsc | LCSC_API_KEY | Not set |
| powrobots: ebay_uk | EBAY_APP_ID | Not set |

---

## Priority fixes

1. ~~Fix powuk ONS URLs~~ → Mark as broken, move on
2. Run powstock with health artifacts → Done
3. Run repair open_repair → Done (13K records)
4. Run powproducts robotshop_uk → Next
5. Add repair remaining collectors → Next
6. Wire powstock to powops health checks → Next
