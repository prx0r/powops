# POW Systems — Mission Control: Complete Development Instructions

Implementation specification

POWOps · POWK · All seven data gardens

Primary repository: [prx0r/powops](https://github.com/prx0r/powops) 

Objective: Transform POWOps into the central operational control system for POW. It must allow one person, or a supervising AI agent, to understand the state of every repository, every collector, every historical backfill and every deployment without manually inspecting individual projects.

I checked the latest available GitHub state of all nine repositories. The instructions below distinguish existing functionality, defects identified in the code and new work required.

The most important requirement is that the dashboard must report demonstrated progress, not activity or self-reported claims from coding agents.

# 1. Project context and scope

POW is building a continuously updated economic model of the physical world. Its current engineering priority is Layer 1: continuously collecting, validating, preserving and monitoring real-world observations.

The existing architecture is:

L1 · Seven independent gardens

powpowpow

powuk

powstock

repair

powproducts

powrobots

powphysical

## POWOps

Operational supervision, collection health, incidents, backups, development and agent control.

## POWK

Deterministic L2 snapshots, historical dependency graphs, evidence and model execution.

POWOps supervises both the independent gardens and the POWK pipeline. It does not take ownership of their domain logic.

The principal deliverable is the existing `admin.pow.systems` dashboard, extended into a genuine mission-control application.

It needs to answer five questions immediately:

1. Which data sources are actually collecting valid observations?

2. How much historical data has been captured, and what's missing?

3. What have the coding agents delivered, and is that code tested and deployed?

4. What is broken, blocked or at risk of data loss?

5. What requires human intervention?

Everything in this project should contribute to answering one of those questions.

## 1.1 Repository responsibilities

| Repository | Ownership | POWOps responsibility |
| --- | --- | --- |
| `powpowpow` | Mining networks, compute and cryptocurrency markets | Check collector health, venue connectivity, archival continuity and backfills |
| `powuk` | UK labour, infrastructure, qualifications, procurement and economic activity | Check source coverage, freshness and geographic/historical completeness |
| `powstock` | Corporate filings, securities and capital markets | Check filings, market-data ingestion, entitlement problems and backfills |
| `repair` | Repair records, physical assets, failures and resale economics | Check raw collection, marketplace ingestion, normalization readiness and history |
| `powproducts` | Product identities, specifications and compatibility | Check catalogue acquisition, validation and identity coverage |
| `powrobots` | Robotics, components, manufacturers and UK market signals | Check live collectors separately from static seed data |
| `powphysical` | Suppliers, prices, component sourcing and manufacturing services | Check supplier collectors, availability of APIs and archival coverage |
| `powk` | Deterministic L2 historical substrate | Check export compatibility, snapshot-building tests and pipeline freshness |
| `powops` | Central operations | Check its own health and the condition of the entire platform |

`powstock` is the actual GitHub repository name, not `powstocks`. `powpowpow` uses `master` as its default branch; the other eight use `main`.

# 2. Initial findings: fix existing problems before adding features

The agent must begin with an evidence-based audit of the current code. Do not rewrite working modules simply because a new architecture is proposed.

Current code review findings

The following are specific problems found in the current repository state, rather than hypothetical future improvements.

| Area | Finding |
| --- | --- |
| Garden registry | POWOps hard-codes 29 sources across only four gardens |
| Incident tracking | Incident filenames use `inc:` while the listing function searches for `inc-*` |
| Heartbeats | A valid JSON heartbeat with no parseable timestamp can incorrectly report `ok` |
| Collection success | Some checks infer success from file modification times or process existence |
| Dashboard | Five views are implemented; comprehensive coverage and development visibility are missing |
| Authentication | API and browser requests still depend on URL query tokens |
| Data integrity | Dashboard describes hashes as independently verified, but its check hashes are not independently verifiable |
| CI | POWProducts' latest GitHub Actions test run failed |
| Backups | R2 coordination still uses four hard-coded garden paths |

Sources: [POWOps health code](https://github.com/prx0r/powops/blob/main/powops/health.py) , [garden readers](https://github.com/prx0r/powops/blob/main/powops/garden.py) , [incidents](https://github.com/prx0r/powops/blob/main/powops/incidents.py) , [dashboard server](https://github.com/prx0r/powops/blob/main/web/server.py) .

There are two additional security checks to prioritize.

The existing `PEER_REVIEW.md` documents an earlier dashboard-token exposure. Verify that the credential was actually rotated; removing it from the current README is insufficient.

Separately, PowPowPow's public repository currently contains 408 `.eml` files under `emails/`. Audit them locally for personal data, private correspondence and credentials. Do not display their contents in logs, reports or agent conversations. If any sensitive information was published, restrict access as appropriate, rotate affected credentials and coordinate removal from Git history.

Do not let the security audit turn into an unrelated feature-development project. Address actual exposure first.

# 3. Phase 0 — Establish a verified baseline

Before modifying anything, produce a machine-readable inventory and a human-readable audit.

Create `reports/baseline/` containing an inventory for all nine repositories.

For each repository, record its default branch, current commit SHA, latest commit date, deployment location, current production SHA if deployed, manifest locations, collectors implemented, tests present, GitHub Actions workflows and their latest results.

Do not infer deployment from the existence of a `systemd` service file.

Run the existing tests against fresh checkouts wherever dependencies and permissions allow. Preserve the complete commands, exit codes and failing-test names. Inspect the latest POWProducts CI failure; do not guess its cause from the GitHub Actions summary.

On the production VPS, establish whether each garden actually exists and where its data lives. Run the existing POWOps commands:

```bash
python3 -m powops status --json
python3 -m powops full --dry-run
python3 -m powops sources
```

Also inspect the relevant `systemd` timers and services, collector-run records, recent failures, raw output directories and R2 backup receipts.

The baseline report must distinguish six states: documented, implemented, tested, deployed, collecting and historically backfilled. A repository can be advanced in one state and entirely unverified in another.

Phase 0 acceptance: A single report identifies every existing garden, the verified operating state of its collectors, the latest code and deployment versions, and every currently known blocker. Unknown information must remain explicitly unknown.

# 4. Phase 1 — Introduce one canonical operational contract

The current POWOps registry duplicates source information already declared in individual repositories. It will drift further as new agents add collectors.

Each garden must own its source definitions. POWOps should discover and consume them, not become another manually maintained collector registry.

## 4.1 Preserve existing manifests

Do not immediately migrate every repository into an entirely new format.

POWUK already has source manifests under `layer1/sources/`. POWStock has manifests under `layer1/sources/`, Repair has `layer1/manifests/`, and POWProducts and POWRobots have their own registries.

Implement small adapters in each repository that expose a common operational manifest, without moving or duplicating the existing domain-specific definitions.

The intended output is a generated, versioned operational manifest such as `ops/manifest.json`.

```json
{
  "schema_version": 1,
  "garden_id": "powuk",
  "repository": "prx0r/powuk",
  "default_branch": "main",
  "sources": [
    {
      "id": "powuk/find_tender",
      "local_id": "find_tender",
      "description": "UK procurement notices",
      "lifecycle": "implemented",
      "schedule": {
        "type": "interval",
        "seconds": 3600
      },
      "historical": {
        "backfill_supported": true
      },
      "health_artifact": "ops/health/find_tender.json"
    }
  ]
}
```

This is an illustrative interface, not an assertion that the named collector currently meets these properties.

## 4.2 Stable source identity

All operational records must use namespaced identifiers:

`garden_id/source_id`

For example, `repair/open_repair` and `powuk/open_repair` are different collectors, even if they use the same upstream dataset.

Store provider identity separately from collector identity. This will allow POWOps to detect shared provider outages without incorrectly merging independent collectors.

## 4.3 Local garden discovery

POWOps should retain only a small registry of garden locations and connection methods. It should load and validate source manifests from the owning repositories.

Support local filesystem discovery initially, followed by an HTTP or agent-hosted endpoint if a garden moves to a different VPS.

A missing manifest is an explicit operational failure, not permission to silently reuse an old central entry.

Provide a migration command that compares the existing 29-source registry with all discovered manifests and produces a reconciliation report. Preserve historical source IDs through an alias mapping rather than silently renaming existing history.

# 5. Phase 2 — Make collection health trustworthy

This is the most consequential backend change.

The current health readers support heartbeat files, SQLite collector runs, file timestamps and PID files. Preserve these as compatibility mechanisms, but distinguish weak operational signals from evidence of successfully collected data.

A live process is not proof of a successful collector. A new file is not necessarily a valid observation. A successful HTTP response is not necessarily valid data.

## 5.1 Required collector-run receipt

Every collector should produce an operational receipt after every attempt. Where possible, it should be written atomically after raw records and their manifest have been durably committed.

```json
{
  "schema_version": 1,
  "run_id": "unique-run-id",
  "garden": "powuk",
  "source_id": "powuk/find_tender",
  "collector_sha": "full-git-sha",
  "started_at": "2026-09-23T09:00:00Z",
  "finished_at": "2026-09-23T09:01:12Z",
  "status": "success",
  "records_seen": 120,
  "records_new": 14,
  "records_updated": 3,
  "records_rejected": 0,
  "raw_bytes_new": 58240,
  "raw_manifest_path": "warehouse/manifests/run-id.json",
  "cursor_before": "previous-cursor",
  "cursor_after": "next-cursor",
  "validation": {
    "passed": true,
    "schema_version": "source-schema-version"
  },
  "error": null
}
```

Source-specific metadata can be added under an extensible field, but avoid changing the meaning of shared fields.

A receipt must be created for failed attempts as well. Capture the failure category and a sanitized error message without recording credentials, request authorization headers or sensitive response bodies.

The operational state store must preserve at least three different timestamps:

* Last attempted run.

* Last successful, validated run.

* Last run that produced new observations.

Also preserve the most recent upstream event timestamp when the source supplies one. These represent different things.

A source can legitimately produce zero new records because nothing changed. In that case, it may still be healthy, but only if it successfully checked the upstream source and validated the response. A collector that simply emitted a new heartbeat must not be treated as having verified the upstream source.

## 5.2 Correct the existing health readers

In `powops/garden.py`, reject missing, malformed or implausibly future-dated heartbeat timestamps rather than returning `ok`.

For SQLite-backed sources, do not populate `last_success` from the latest failed attempt's start time. Query the latest attempt and latest validated success independently.

Treat `raw_mtime` and `pid_file` as weak compatibility checks. Label their evidence level accordingly; do not allow them to satisfy the stronger `collecting_verified` requirement.

The current central `no_key` check reads POWOps' own environment. That can produce misleading results if a collector receives credentials through a different service environment. Prefer a sanitized status reported by the owning collector, while never exposing secret values.

## 5.3 Separate lifecycle from health

Use two independent state dimensions.

| Lifecycle | Meaning |
| --- | --- |
| Planned | Required by the source plan, but not implemented |
| Implemented | Collector exists |
| Tested | Required tests have passed |
| Deployed | A specific collector revision exists in the deployment |
| Collecting | Validated collection has been observed |
| Backfilling | Historical capture is underway |
| Complete for target | Defined historical coverage target has been met |

Runtime health should independently express `healthy`, `stale`, `error`, `blocked`, `not_due` or `unknown`.

This prevents an unimplemented source from disappearing from coverage calculations and prevents a process that is running but collecting nothing from displaying as complete.

Schedule-aware health is essential. Annual publications, hourly APIs, monthly filings and real-time WebSockets cannot all use the same freshness threshold.

# 6. Phase 3 — Track actual historical growth

POW's Layer 1 checkpoint is not simply that collectors can run. It is that useful history is being continuously accumulated and preserved.

Build a historical-coverage subsystem that operates independently of runtime health.

Each garden should report cumulative validated records and bytes, earliest and latest observation times, earliest and latest acquisition times, completed historical partitions, outstanding partitions, backfill errors and the last archived manifest.

For sources with a known target interval, display coverage against that interval. For sources where upstream history is unavailable or poorly documented, do not manufacture a completion percentage.

## Example: source detail

Illustrative

POWUK / Procurement notices

Runtime

Healthy

Backfill target completed

# 68%

Latest successful ingestion

12 minutes ago

Archive verification

Pending

These numbers illustrate the proposed interface only; they are not live collector measurements.

The volume subsystem must distinguish cumulative total records from new records per run. Do not compare a cumulative database row count to yesterday's incremental fetch count or treat an unchanged cumulative count as evidence of failure.

Track historical revisions and deduplication. Raw observations must remain reconstructable, with content hashes, source identifiers, acquisition timestamps and rights or retention metadata.

Prioritize inexpensive durable storage and R2 archiving over complex analytics.

# 7. Phase 4 — Build the complete mission-control dashboard

Retain the existing lightweight dashboard instead of beginning another frontend application.

Its current five views should be extended into a coherent operator interface. Share backend services between the web interface, CLI and MCP so they cannot disagree about the same source's status.

# Proposed navigation

Overview

System-wide collection and deployment state

Gardens

Every source, latest run and backfill

Development

Repositories, commits, tests and deployments

Incidents

Open problems and recovery history

History

Freshness, throughput and outages

Backups

Archive continuity and restore tests

Agent activity

Pi investigations and proposed actions

System

Configuration and operational diagnostics

## 7.1 Overview

The landing page must answer the owner's operational questions within a few seconds.

Show total planned sources, implemented sources, verified active sources, failed sources, historical backfill progress where measurable, most recent successful collection, archive status and open incidents.

A separate development strip should show repositories with failing CI, deployments behind their default branch and agents waiting for input.

The most important panel is Action required. It should aggregate actual blockers and incidents rather than generating generic AI recommendations.

Do not use an overall green banner merely because every currently installed collector returned a heartbeat. Missing planned sources and unverified archives must remain visible.

## 7.2 Gardens

Display seven garden summaries and drill down into every registered source.

Provide filters for lifecycle, health, cadence, blocked reason, backfill status and latest successful run.

Each source-detail page should show its owner repository, source manifest, latest run receipt, recent run history, data growth, schema version, raw archive manifest, operational incidents and available diagnostics.

Add links to the corresponding GitHub source files and logs, but never expose raw secrets or private request payloads.

## 7.3 Development

Create a dedicated GitHub integration using the existing nine-repository inventory.

Use the GitHub API to retrieve default branches, latest commits, relevant workflow results, open pull requests and release or deployment information where available. Cache results, handle rate limits and respect API error states. Do not interpret an empty workflow list as passing CI.

Represent code and production deployment versions independently. The deployment SHA must originate from an actual deployment receipt or a verified running process, not a repository README.

A useful repository row should display:

`repository | latest commit | latest CI | deployed SHA | collection status | open blocker`

Allow drill-down into recent changes and test results.

Agent assignments should be sourced from explicit GitHub issues, pull requests or a small maintained task registry. Do not invent a current task or agent status by interpreting a commit message.

## 7.4 Backups and incidents

Build first-class backup status into the dashboard, with latest attempt, latest verified success, remote object or manifest verification, bytes archived, failures and last successful restore drill.

For incidents, expose severity, source, opening time, last validated success, current error, timeline, assigned owner, diagnostic evidence and resolution status.

These should be operational records shared with the Pi agent, not separate browser-only state.

# 8. Phase 5 — Durable operational storage

Keep POWOps' operational database separate from the domain data warehouses.

SQLite with WAL is sufficient for the initial single-VPS deployment. Avoid introducing distributed infrastructure without a demonstrated requirement.

Introduce or consolidate durable tables for:

| Table | Purpose |
| --- | --- |
| `gardens` | Repository and deployment identities |
| `sources` | Normalized manifest records |
| `collector_runs` | Immutable run receipts |
| `source_state` | Current derived operational state |
| `backfill_partitions` | Historical coverage and checkpoints |
| `repo_snapshots` | GitHub and deployment observations |
| `backup_runs` | Archive receipts and verification |
| `incidents` | Durable incident state |
| `events` | Append-only operational events |
| `agent_actions` | Proposed and executed action receipts |

Use unique run IDs and idempotent ingestion. Replaying the same receipt must not inflate data-growth totals or create duplicate incidents.

Separate immutable observations from derived current status. A repaired source should close its active incident while retaining the full outage history.

Fix the existing `incidents.py` filename/glob mismatch. Use a unique incident identifier that permits repeat outages on the same day, and prevent concurrent health cycles from creating duplicates.

The existing daily JSONL operational history can remain as an export or compatibility layer. Its hash chain is not independent proof of authenticity: an attacker with write access can rewrite an unkeyed chain. Remove claims that timestamps or records cannot be forged merely because they contain hashes.

If tamper evidence is required, periodically anchor signed or keyed manifests outside the writable operational store.

# 9. Phase 6 — Complete the MCP interface for Pi

POWOps already has a read-only MCP implementation for status, history, uptime, incidents, coverage, schemas, verification and events. Extend that implementation rather than creating another parallel agent API.

Expose structured, versioned results for the following capabilities:

```
powops_overview
powops_gardens
powops_sources
powops_source_detail
powops_collector_runs
powops_backfill_status
powops_repository_status
powops_deployment_status
powops_incidents
powops_incident_detail
powops_backup_status
powops_recent_events
powops_diagnose
```

Implement `powops_diagnose` as a deterministic diagnostic pipeline first. It should compare actual operational evidence with configured expectations and produce possible causes, relevant evidence and suggested next checks.

An LLM can summarize those findings, but it must not fabricate a root cause.

The initial agent workflow should be read-only:

```
1. Read operational events.
2. Retrieve current source and repository states.
3. Identify new failures or material changes.
4. Retrieve relevant run receipts and sanitized logs.
5. Correlate failures sharing an upstream dependency.
6. Open or update a durable incident.
7. Prepare a concise human report.
8. Propose any remediation requiring authorization.
```

Do not implement unrestricted arbitrary-shell execution, arbitrary URL fetching, secret retrieval or automatic deployment through the MCP server.

Future write actions should use explicit allowlists, separate permissions, human approval where appropriate, idempotency keys and durable execution receipts. Restarting a known collector is a different authorization class from changing its code or deleting data.

The dashboard must display both the agent's proposed action and the evidence supporting it. An agent's assertion that a problem is fixed is not a recovery signal; POWOps must independently verify the subsequent collector runs.

# 10. Phase 7 — CI, deployment and security

Add CI to POWOps and introduce minimal standardized CI checks across the other repositories, working with the owners of those repositories rather than rewriting their entire build systems.

For POWOps, CI should cover unit tests, contract tests, API tests, MCP integration and linting. On the VPS, run separate smoke tests against the installed collectors and actual storage.

Do not require public GitHub Actions to access production secrets merely to establish that a commit passes local unit tests.

## 10.1 Secure the dashboard

The remote dashboard should be protected by Cloudflare Access in front of the existing loopback-bound service and Cloudflare Tunnel.

Remove URL-query authentication from the normal remote browser flow. If local bearer-token authentication remains necessary, use authorization headers, secure token storage and constant-time comparisons.

Do not trust identity headers supplied directly by an external client. Ensure the origin is inaccessible except through the intended trusted access path.

The current dashboard also embeds JavaScript and CSS while returning a restrictive Content Security Policy. Resolve that inconsistency by serving separate static assets or using a correctly configured nonce or hash policy. Avoid weakening the policy unnecessarily.

Replace the current partial HTML escaping with safe DOM construction for any source names, descriptions, errors or other externally influenced values.

Bound API parameters and response sizes, and redact secrets and sensitive paths from logs.

## 10.2 Deployment

Retain the existing `systemd`-based architecture where practical. Harden service permissions and restart behavior, expose a meaningful readiness check and ensure the health timer is enabled.

POWOps needs an independent external watchdog. If the entire VPS or POWOps process goes down, it cannot reliably send its own outage alert.

Every deployment should record the exact commit SHA, time, operator or agent, migration version, test result and post-deployment smoke-test result.

Back up the operational database, but prioritize recovery of the actual gardens' irreplaceable raw history.

# 11. Required tests and failure simulations

The testing requirement is not simply a high count of passing unit tests. It must demonstrate that POWOps reports real failures correctly and that it never converts missing evidence into a false success.

## Minimum acceptance test suite

Verification checklist for the coding agent

0/18

Collector health

Missing or malformed heartbeat is not healthy

A live PID with no validated data is not marked collecting

Latest failure does not overwrite last successful run

Expected zero-new-record run is distinguishable from an unverified run

Missing credentials, rate limits and invalid upstream data report distinct failures

Registry and coverage

All seven gardens are discovered

Duplicate or conflicting source identifiers are rejected

A planned but unimplemented source remains in coverage reports

Garden manifest changes are detected without editing POWOps' central source list

History and incidents

Run-receipt replay is idempotent

Repeated same-day outages create independent incident lifecycles

Incident recovery requires verified successful collection

Unknown and not-installed sources cannot produce an all-healthy summary

Infrastructure and API

Failed R2 backups remain visible

An archive restore test is recorded

GitHub CI absence is not treated as passing

Unauthorized API requests are rejected

Dashboard, CLI and MCP return consistent source states

Also test interrupted historical backfills, invalid cursors, duplicate observations, upstream API pagination changes, expired credentials, schema drift, corrupt operational records, concurrent health cycles and disk exhaustion where safe to simulate.

Do not run destructive failure simulations against irreplaceable production data. Use isolated fixtures, a staging state directory or disposable database copies.

A full production acceptance run must include a continuous monitoring window and at least one controlled failure-and-recovery exercise. For infrequently updated datasets, use an appropriate collection or backfill verification rather than claiming that 24 hours of inactivity constitutes a failure.

# 12. Development sequence and deliverables

Execute this work in the following order. Do not begin with a frontend redesign.

| Sequence | Deliverable | Exit condition |
| --- | --- | --- |
| P0 | Baseline and security audit | Nine-repository inventory, verified runtime state and security findings |
| P1 | Health correctness | False-green defects fixed and covered by tests |
| P2 | Garden discovery | All seven gardens registered from owner-controlled manifests |
| P3 | Collection and backfill receipts | Actual ingestion progress is measurable |
| P4 | Durable incidents and backup state | Failures, recovery and archival state survive restarts |
| P5 | Development integration | GitHub and actual deployment state visible |
| P6 | Mission-control dashboard | All major operational views use the same backend |
| P7 | MCP and Pi integration | Read-only diagnostics and structured reporting work |
| P8 | Production validation | End-to-end tests, monitoring evidence and recovery tests pass |

Keep changes reviewable. Prefer a series of small pull requests over a single enormous commit.

Each completed phase must include its changed files, exact test commands and results, representative output, deployment instructions, migration or rollback procedure and any remaining limitations.

Where work requires changes to another repository, create a clearly specified cross-repository task rather than copying that repository's logic into POWOps.

## Definition of done

The mission-control project is ready for its first operational release when the dashboard can show every POW garden, distinguish implemented collectors from verified collectors, display real historical growth and archive status, identify failing code or deployments, and present durable incidents requiring attention.

The Pi agent must be able to read that same state and generate a grounded operational report without manually inspecting seven repositories.

Do not claim checkpoint-one completion merely because the dashboard is finished. The dashboard is the instrument used to establish which gardens have reached checkpoint one. It should make unfinished work and missing evidence unavoidably visible.

The first action is the baseline inventory and production verification. Once that report exists, fix health correctness and manifest discovery before building new dashboard views.
