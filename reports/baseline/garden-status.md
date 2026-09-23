# Garden Collection Status — 2026-09-23

## Overall: 1 of 7 gardens actually collecting

```
Collecting:     powpowpow (807K files, 3 services running)
Partially:      repair (4 files, no DB tables), powrobots (11 files, no DB)
Empty:          powproducts, powphysical
Manifests only: powuk, powstock (no collectors implemented)
```

## Per-garden detail

### powpowpow — COLLECTING
- **Raw files:** 807,932 (venue: 800K, qubic: 3.8K, xmr: 4.2K, kas: 3.2K, etc.)
- **Running services:** pow-chain-state, pow-venue-l2, pow-venue-ws
- **Failed services:** pow-daily-state, pow-qubic-computors, pow-qubic-epoch, pow-seed-rebuild, pow-tardis-reload, pow-tardis-remainder
- **Status:** Healthy core collectors running. 6 auxiliary services failed.

### repair — PARTIAL
- **Raw files:** 4 (1 open_repair CSV, 3 test_source blobs)
- **Database:** Exists but EMPTY — no tables, no collector_run records
- **Status:** Has collector infrastructure but no actual collection happening. The open_repair file is a single CSV snapshot.

### powrobots — PARTIAL
- **Raw files:** 11 across 10 sources (bara_directory, bgs_minerals, contracts_finder, find_apprenticeship, hmrc_trade, hmrc_traders, ons_ppi, opss_safety, rbtx, ukri_gtr)
- **Database:** Exists but EMPTY — no tables
- **Collector code:** BaseCollector is importable. Collectors exist for all 15 sources.
- **Status:** Has run at least once (raw files exist) but DB schema was never initialized or wiped.

### powproducts — EMPTY
- **Raw files:** 0
- **Database:** Exists but EMPTY — no tables, no data
- **Collector code:** 8 collectors implemented (robotshop_uk ready, 7 planned)
- **Status:** Collector infrastructure built but never successfully run.

### powphysical — EMPTY
- **Raw files:** 0
- **Database:** Does not exist
- **Adapters:** 3 adapter stubs (lcsc, m5stack, waveshare) — all fixture-only
- **Status:** Skeleton repo. No data collection at all.

### powuk — MANIFESTS ONLY
- **Raw files:** 0
- **Database:** Does not exist
- **Warehouse:** Does not exist
- **Source manifests:** 16 YAML files (ch_capacity, contracts_finder, ons_salaries, etc.)
- **Collector implementations:** NONE — collectors/__init__.py is empty
- **Running services:** NONE
- **Status:** Has source specifications but no working collectors. The BaseCollector class exists in layer1/collector.py but can't be imported (design mismatch).

### powstock — MANIFESTS ONLY
- **Raw files:** 0 (except k3_export which is L2 data)
- **Database:** Does not exist
- **Source manifests:** 15 source directories under layer1/sources/
- **Collector implementations:** Registry and health modules exist, no actual collectors
- **Status:** Has source specifications and L2 export data but no L1 collection.

## Cross-garden dependencies

| Consumer | Needs from powuk | Status |
|----------|-----------------|--------|
| powrobots | ch_capacity (UK business data) | powuk has manifest, no collector |
| powproducts | open_repair (repair demand signals) | powuk has no open_repair source at all |
| powphysical | ons_salaries (regional cost intelligence) | powuk has manifest, no collector |
| repair | open_repair, contracts_finder | powuk has contracts_finder manifest, no open_repair, no collectors |

**Critical gap:** powuk is the dependency bottleneck. Four gardens need data from powuk, but powuk has zero working collectors and zero data.

## What needs to happen

1. **powuk collectors must be implemented.** The 16 source manifests exist but there are no working collector scripts. This blocks powrobots, powproducts, powphysical, and repair.

2. **powrobots DB must be initialized.** The raw files exist but the database has no tables. The collector code is importable.

3. **repair DB must be populated.** The database exists but has no tables. One open_repair CSV exists but isn't parsed into the DB.

4. **powproducts must run its first collector.** The robotshop_uk collector is marked "ready" but has never produced output.

5. **powphysical needs actual adapters.** The three adapter stubs return fixture data. No real supplier integration exists.

## Priority order

1. powuk — implement at least contracts_finder and ons_salaries collectors (unblocks 4 gardens)
2. powrobots — initialize DB schema, run existing collectors
3. repair — initialize DB tables, parse open_repair CSV
4. powproducts — run robotshop_uk collector
5. powphysical — implement real LCSC adapter
