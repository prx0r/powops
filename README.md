# powops

Layer 1 command centre for POW gardens.

> Are the gardens alive?

No economics. No modelling. No Seesaw. Just operational observability
across all Layer 1 data ingestion.

## Quick Start

```bash
cd /home/ubuntu/powops
python3 -m powops status
```

## What It Does

Reads health artifacts from each garden and shows a unified status table:

```bash
$ python -m powops status

POWOPS — Layer 1 Command Centre  2026-09-21 18:30 UTC

  Overall: ALL SYSTEMS OPERATIONAL

  GARDEN       SOURCE                LAST GOOD    AGE        STATUS
  ──────────────────────────────────────────────────────────────────
  powpowpow    chain_state           18:25        5m         ok
               venue_l2              18:28        2m         ok
               venue_ws              18:27        3m         ok
               daemon                18:29        1m         ok
  ──────────────────────────────────────────────────────────────────
  repair       open_repair           06:00        12h        ok
               cex_pricing           12:00        6h         ok
               trade_pricing         18:30        0m         ok
               robotshop             18:28        2m         ok
               partsdb               ---          ---        no_key
               opss_recalls          06:00        12h        ok
  ──────────────────────────────────────────────────────────────────

  9/10 sources OK | powpowpow: 4/4 ok | repair: 5/6 ok, 1 issues
```

## Commands

```bash
python -m powops status           # Table view
python -m powops status --json    # JSON output
python -m powops sources          # List all configured sources
python -m powops check venue_l2   # Check one source
python -m powops backup           # Sync raw data to R2
```

## How It Works

1. **sources.yaml** declares every source across all gardens
2. Each source has a `health.check` type:
   - `heartbeat` — reads a JSON file with `heartbeat_at` timestamp
   - `collector_db` — queries SQLite `collector_run` table
   - `raw_mtime` — checks file modification times
   - `pid_file` — checks if a process is alive
3. **garden.py** reads each garden's artifacts
4. **health.py** aggregates into a unified status list
5. **status.py** renders the table

## Adding a New Garden

1. Add the garden to `sources.yaml` under `gardens:`
2. Add its sources under `sources:`
3. Implement a health artifact reader in `garden.py` if needed
4. Done — `pow status` picks it up automatically

## File Layout

```
powops/
├── sources.yaml       # Universal source manifest
├── garden.py          # Per-garden health readers
├── health.py          # Cross-garden aggregation
├── status.py          # CLI table rendering
├── backup.py          # R2 sync coordination
├── __main__.py        # CLI entry point
├── deploy/systemd/    # Optional periodic snapshots
└── tests/             # Test suite
```

## Tests

```bash
python3 -m pytest tests/ -v
```
