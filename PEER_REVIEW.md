# POWOPS + POWK — Peer Review

Reviewed against current latest pushes:

```text
powops
latest: e666ef31...
dashboard + MCP + four gardens wired

powk
latest: 20a33c37...
P0 content-addressing / snapshots / determinism fixes
```

The overall architecture is now substantially correct:

```text
REALITY
  │
  ▼
LAYER 1 GARDENS
powpowpow
powuk
powstock
repair
  │
  ├──────────────→ POWOPS
  │                 operational supervision
  │
  ▼
L1 EXPORTS
  │
  ▼
POWK
Layer 2 deterministic historical substrate
  │
  ▼
MODELS / RESEARCH
Layer 2B / Layer 3
```

Do not collapse these layers again.

---

# Executive assessment

## POWOPS

The latest push is directionally excellent.

It now genuinely functions as an operator surface rather than just documentation:

```text
CLI
health history
uptime
volume
schema monitoring
alerts
dashboard
MCP
systemd
```

That is the correct home for these functions.

However, five structural issues remain:

```text
1. A live secret has been committed publicly.
2. sources.yaml is still becoming a duplicated central source registry.
3. dashboard authentication is too weak for admin.pow.systems.
4. MCP currently reports but lacks a proper incident/action architecture.
5. health reporting still needs stronger collection semantics:
   last_attempt vs last_success, coverage, backup state, etc.
```

The dashboard itself is useful and should stay.

The MCP server is also exactly the right direction.

But both should remain views/control surfaces over POWOps rather than evolving independent logic.

---

# POWK

The latest P0 pass fixed most of the issues identified in the last review:

```text
✓ model file hashing
✓ observation IDs include values/revisions
✓ evidence IDs strengthened
✓ content-addressed Store
✓ append-only Graph
✓ deterministic revision ordering
✓ evidence look-ahead checks
✓ model-defined unknown requirements
✓ scenario replacing implicit shock model
✓ substantially expanded invariant tests
```

Very good.

There are still a few important correctness problems:

```text
1. Structural knowledge-time is still incomplete.
2. snapshot world/knowledge observation filtering has a subtle bug.
3. Edge still carries coefficient/coefficient_unit.
4. adapters are currently inventing invalid REQUIRES relationships.
5. adapters hard-code filesystem paths.
6. adapter aggregation destroys historical granularity in places.
7. build_snapshot.py contains model/research behavior that shouldn't be adapter code.
```

The adapter problem is the biggest new concern.

---

# CRITICAL — immediately rotate the dashboard secret

The current public README contains a live dashboard URL including its token.

Assume that token is compromised.

Do this immediately:

```text
1. Rotate POWOPS_TOKEN.
2. Remove the token-bearing URL from README.
3. Do not print the real token in documentation.
4. Prefer removing it from git history as well.
5. Check Cloudflare logs/access logs if available.
```

Never put:

```text
https://admin.pow.systems/?token=<secret>
```

into GitHub.

README should only say:

```text
https://admin.pow.systems/
```

---

# DASHBOARD REVIEW

The dashboard is useful enough to keep.

Do NOT remove it in pursuit of architectural purity.

Its purpose is:

> Human control panel for Layer 1.

It should become the visual equivalent of:

```bash
powops status
```

not an analytics application.

---

# Dashboard auth — P0

Current authentication is:

```text
?token=<secret>
```

on every request.

This has multiple problems.

Query-string secrets can appear in:

```text
browser history
Cloudflare request logs
proxy logs
referrer headers
screenshots
copied URLs
shell history
README files
```

The public token exposure already demonstrates the failure mode.

## Preferred architecture

Use Cloudflare Access in front of:

```text
admin.pow.systems
```

and keep the origin:

```text
127.0.0.1:8796
```

Then:

```text
Internet
   ↓
Cloudflare Access
   ↓
Cloudflare Tunnel
   ↓
127.0.0.1:8796
```

POWOps does not need to build an authentication system.

For local direct access, optionally retain token auth.

But:

```text
remote public access → Cloudflare Access
local access → loopback/token optional
```

Do not make the query token the main auth mechanism.

---

# Dashboard HTTP hardening

Add:

```text
Cache-Control: no-store
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy
```

The dashboard displays operational information and should never be browser-cached aggressively.

Also stop printing the token to journald.

Current startup output includes the complete token-bearing URL.

That turns:

```text
journalctl --user -u powops-dashboard
```

into another credential store.

Print:

```text
POWOps dashboard listening on 127.0.0.1:8796
```

only.

---

# Dashboard HTML safety

Current `esc()` only replaces `<`.

Use complete HTML escaping or, preferably, stop constructing HTML from arbitrary strings and populate cells using:

```javascript
element.textContent = value
```

Source names/errors eventually contain data fetched from third parties.

Don't assume they are trusted.

This is especially relevant for:

```text
error strings
source descriptions
authority strings
schema fields
```

---

# Dashboard API input bounds

These should be clamped:

```text
days
history lengths
timeline lengths
volume ranges
```

Do not allow:

```text
/api/history?days=999999999
```

to read effectively unlimited history.

Suggested:

```text
days min = 1
days max = 365
default = 7
```

---

# Dashboard status cache

30 seconds is fine.

But `_cached_status()` may be executed by multiple request threads simultaneously.

Add a simple lock around refresh.

Not because this is a high-scale service, but because health checks may touch multiple SQLite databases/files.

---

# What the dashboard should show

Do not turn it into Grafana.

Keep it extremely operational.

I would settle on six views:

```text
STATUS
COVERAGE
INCIDENTS
VOLUME
SCHEMAS
BACKUPS
```

And optionally:

```text
SOURCE DETAIL
```

as a drill-down rather than its own tab.

---

# STATUS

Current status view is right.

Expand each row to expose:

```text
garden
source
status
last_attempt
last_success
age
records_new
bytes_new
collector_version
```

Current:

```text
last_good
records
```

is too ambiguous.

---

# COVERAGE

This is missing and is important.

Health and completeness must remain separate.

Example:

```text
POWUK

planned priority sources: 42
installed:                29
healthy:                  27
blocked:                   2
not implemented:          11
```

This gives us Checkpoint 1 progress.

The dashboard must never say:

```text
ALL SYSTEMS OPERATIONAL
```

and imply:

```text
Layer 1 complete.
```

Those are different statements.

---

# INCIDENTS

Introduce an explicit incident abstraction in POWOps.

This will become the foundation for the Pi agent.

Example:

```json
{
  "incident_id": "inc:20260922:powuk:neso",
  "source_id": "neso",
  "garden": "powuk",

  "opened_at": "...",
  "resolved_at": null,

  "status": "open",
  "severity": "warning",

  "reason": "stale",
  "last_success": "...",

  "current_error": "...",

  "events": []
}
```

Incident transitions:

```text
healthy
   ↓
problem detected
   ↓
INCIDENT OPEN
   ↓
updates appended
   ↓
recovery verified
   ↓
INCIDENT CLOSED
```

This is much better than asking an agent to infer conversations from raw health history.

---

# BACKUPS

Add first-class backup status to dashboard:

```text
garden
last backup attempt
last successful backup
files uploaded
bytes uploaded
remote verification
restore-test state
```

For the garden thesis, backup health is nearly as important as collector health.

If we're collecting irreplaceable history:

```text
collector alive
+
archive dead
=
not healthy
```

---

# SOURCE DETAIL

Clicking a source should expose:

```text
description
authority
cadence
status
last 24h runs
last error
volume history
schema versions
backup state
incident history
collector git SHA
raw data path
```

But do NOT add domain data.

For NESO:

```text
show ingestion health
```

not:

```text
show UK grid constraint model
```

That belongs later.

---

# POWOPS CENTRAL MANIFEST — still needs fixing

The current latest push expanded central `sources.yaml` to 29 sources.

This is useful operationally today but structurally still wrong long term.

We now have:

```text
repair knows its collectors
powuk knows its collectors
powstock knows its collectors
powpowpow knows its collectors

AND

powops knows everybody's collectors
```

That will drift.

---

# Final manifest architecture

Each garden owns:

```text
ops/sources.yaml
```

Example:

```yaml
garden: powuk
protocol: powops/1

sources:

  neso_demand:
    authority: NESO
    cadence: 30m

    health:
      adapter: pow_health_v1
      max_staleness: 90m

    coverage:
      tier: A
      expected: true

    backup:
      include:
        - data/raw/neso_demand
```

POWOps owns only:

```yaml
gardens:

  powuk:
    path: /srv/pow/repos/powuk

  repair:
    path: /srv/pow/repos/repair

  powpowpow:
    path: /srv/pow/repos/powpowpow

  powstock:
    path: /srv/pow/repos/powstock
```

Then:

```text
powops discovers:
<garden>/ops/sources.yaml
```

For now maintain compatibility with existing central manifest.

But do not keep adding future gardens exclusively to the central file.

---

# Standard Layer-1 health artifact

This should become the preferred mechanism.

Each collector writes:

```json
{
  "protocol": "pow-health/1",

  "garden": "powuk",
  "source_id": "neso_demand",

  "last_attempt": "...",
  "last_success": "...",

  "attempt_status": "ok",

  "records_seen": 4153,
  "records_new": 28,

  "bytes_seen": 1938219,
  "bytes_new": 19833,

  "source_timestamp": "...",

  "schema_hash": "sha256:...",

  "raw_artifact_count": 28,

  "collector_version": "git:abc123",

  "error": null
}
```

This is the interface between a garden and POWOps.

Once each garden emits this, POWOps no longer needs to understand:

```text
repair SQLite internals
powpowpow heartbeat files
powuk filesystem layout
```

Those adapters can remain compatibility layers.

---

# Current collector DB fallback

The latest addition to support both:

```text
collector_run
collection_runs
```

is useful pragmatically.

But this should be temporary.

Do not allow `garden.py` to accumulate:

```python
if repair:
if powuk:
if powstock:
```

forever.

The health artifact is the escape hatch.

---

# LAST ATTEMPT vs LAST SUCCESS

Still make this explicit everywhere.

Example:

```text
last_attempt:
05:40

last_success:
03:10

current_status:
error
```

This allows correct answers to:

```text
Is it running?
When did it last work?
When did it last try?
```

Those are different questions.

---

# POWOPS MCP — keep this

This is one of the strongest additions in the latest push.

The conceptual boundary is correct:

```text
Pi / harness
      │
      ▼
POWOps MCP
      │
      ▼
Layer-1 operational state
```

This is exactly how an autonomous operator should access POW.

---

# But pin the MCP dependency

`powops/mcp.py` imports:

```python
mcp.server...
```

while `pyproject.toml` currently contains only:

```text
pyyaml
```

Therefore a clean `pip install -e .` does not guarantee MCP works.

Fix this.

Preferred:

```toml
[project.optional-dependencies]
mcp = [
    "mcp==<tested-version>"
]
dev = [
    "pytest"
]
```

Then:

```bash
pip install -e '.[mcp]'
```

If MCP is considered a core feature, make it a normal dependency instead.

But **pin or tightly constrain the tested SDK version** because MCP Python APIs have changed before.

---

# MCP integration test

Unit tests are not enough.

Create an integration smoke test that:

```text
starts powops MCP over stdio
performs initialize handshake
lists tools
invokes powops_status
receives valid response
shuts down
```

This catches SDK API drift immediately.

---

# MCP output should become structured

The current tools return JSON strings.

This works, but an agent will operate more reliably with structured results.

Where supported by the pinned MCP SDK, return structured dictionaries.

Conceptually:

```json
{
  "overall": "degraded",
  "sources": [...],
  "incidents": [...]
}
```

rather than escaped JSON inside text.

Keep a human-readable text summary if useful, but structure should be authoritative.

---

# Final read-only MCP tool set

I would expose:

```text
powops_status
powops_source
powops_incidents
powops_diagnose
powops_history
powops_uptime
powops_coverage
powops_backup_status
powops_schema_status
powops_logs
```

Some are additions to current six.

---

# powops_status

Answer:

> What is broken right now?

Return only important aggregate state by default.

Optional:

```text
garden
status
```

filters.

---

# powops_source

Current `powops_check`.

Rename eventually for consistent noun semantics.

Return:

```text
source metadata
last_attempt
last_success
current status
latest error
volume
schema
backup status
open incident
```

This should become the single source-detail call.

---

# powops_incidents

The agent will use this constantly.

Arguments:

```text
status=open|closed|all
garden
severity
since
```

Output should include durable incident IDs.

---

# powops_diagnose

Current implementation is too shallow:

```text
stale → "check collector"
```

That's not real diagnosis.

Build deterministic diagnostic evidence first.

For example:

```text
source stale
↓
systemd unit status
↓
last attempt
↓
last error
↓
recent logs
↓
credential presence
↓
raw directory mtime
↓
network/source reachability if configured
```

Return:

```json
{
  "incident": "...",

  "facts": [
    "last success 4h ago",
    "service active",
    "last 3 runs returned HTTP 403"
  ],

  "likely_classes": [
    "upstream_access_failure"
  ],

  "suggested_checks": [...]
}
```

Do not have POWOps itself generate free-form LLM diagnoses.

The Pi agent can interpret deterministic facts.

---

# powops_logs

Very useful for the agent.

Arguments:

```text
source_id
lines = 100
since
```

But never expose arbitrary filesystem paths.

Garden manifest specifies the permitted log source:

```yaml
logs:
  systemd_unit: powuk-neso.service
```

or:

```yaml
logs:
  file: /srv/pow/logs/powuk/neso.log
```

MCP can only access registered sources.

---

# MCP ACTION TOOLS — later, carefully

Right now MCP is read-only.

That is good.

Do not jump immediately to:

```text
run arbitrary shell command
edit source code
restart anything
```

Instead introduce a small action contract later.

Potential tools:

```text
powops_run_source
powops_restart_source
powops_backup_now
powops_backup_verify
powops_ack_incident
```

Never:

```text
powops_shell(command)
```

That destroys the entire safety boundary.

---

# Action authorization model

Default:

```text
READ ONLY
```

Explicit config:

```yaml
agent_actions:

  run_source:
    enabled: true

  restart_source:
    enabled: true
    allow:
      - neso_demand
      - open_repair

  deploy:
    enabled: false

  shell:
    enabled: false
```

The MCP server reads this allowlist.

---

# Every action produces a receipt

Example:

```json
{
  "action_id": "act:...",
  "incident_id": "inc:...",

  "requested_at": "...",
  "requested_by": "pi",

  "action": "restart_source",
  "source_id": "neso_demand",

  "result": "ok",

  "verification": {
    "service_active": true,
    "new_success_observed": true
  }
}
```

Append these to POWOps state.

This gives us:

```text
problem
→ agent action
→ result
→ verified recovery
```

rather than autonomous invisible mutation.

---

# Future Pi agent architecture

Do NOT put Pi itself inside POWOps.

Architecture:

```text
                    YOU
                     ▲
                     │ conversation
                     │
                PI HARNESS
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   POWOPS MCP     POWK MCP     other tools
   operations     analysis     communication
        │            │
        ▼            ▼
    Layer 1        Layer 2
```

POWOps exposes operational truth.

Pi decides what to tell you.

Communication remains a harness concern.

---

# How Pi talks to you

Do not teach POWOps how to send conversational messages.

Instead Pi has whatever communication adapter the harness supports:

```text
Telegram
Slack
email
web chat
push notification
etc.
```

Then Pi can do:

```text
POWOps:
NESO collector stale 3h
HTTP 403
service still active

      ↓

Pi:
"NESO ingestion has failed three times since 02:10.
The process is alive but the upstream endpoint returns 403.
No data has been lost locally.
Want me to restart it or leave it for investigation?"
```

That is the correct separation.

---

# Ideal autonomous monitoring loop

Eventually:

```text
every health cycle
      │
      ▼
POWOps updates state
      │
      ├── no incident
      │      ↓
      │    silence
      │
      └── incident opens/changes
             ↓
          Pi sees event
             ↓
       deterministic diagnosis
             ↓
       classify importance
             ↓
         tell user
             ↓
       propose action if useful
             ↓
       action approval if required
             ↓
       execute via typed MCP tool
             ↓
       verify new successful data
             ↓
       tell user resolved
```

This is much better than having a cron prompt the agent every five minutes.

---

# Event feed for Pi

Create an append-only event stream:

```text
~/.powops/events/YYYY-MM-DD.jsonl
```

Events:

```text
source_stale
source_error
source_recovered
schema_changed
volume_anomaly
backup_failed
backup_verified
incident_opened
incident_updated
incident_closed
```

Example:

```json
{
  "event_id": "evt:...",
  "at": "...",
  "type": "source_stale",
  "garden": "powuk",
  "source_id": "neso",
  "incident_id": "inc:..."
}
```

This becomes far more useful for the agent than polling the entire status table repeatedly.

Future MCP:

```text
powops_events(since=...)
```

---

# Dashboard and Pi share the same state

Very important:

Do NOT separately implement:

```text
dashboard incident logic
MCP incident logic
CLI incident logic
```

One core library should produce state.

Then:

```text
CLI ────────┐
Dashboard ──┼── powops core
MCP ────────┘
```

That prevents inconsistencies.

---

# POWK — remaining correctness review

The P0 pass is much improved.

However, fix these before declaring v0.2 complete.

---

# POWK P0.1 — structural knowledge time is still not implemented

`Graph.build_snapshot()` contains:

```python
if mode == "knowledge" and hasattr(edge, 'observed_at')
```

but current `Edge` dataclass does not define:

```text
observed_at
```

Likewise `Node` has:

```text
valid_from
valid_to
```

but no knowledge-time field.

Therefore this invariant from SPEC is not actually satisfied:

> reconstruct what we knew at time t.

A dependency discovered later can leak backwards.

Fix Node and Edge:

```text
effective_from
effective_to
observed_at
```

or minimally:

```text
valid_from
valid_to
observed_at
```

Then knowledge snapshot:

```text
observed_at <= t
```

must be mandatory.

Do NOT rely on `hasattr`.

---

# POWK P0.2 — snapshot observation condition is wrong

Current code effectively checks:

```python
if o.effective_at > at and o.observed_at > at:
    continue
```

This means in world mode an observation with:

```text
effective_at = future
observed_at = past
```

could be admitted.

World-time snapshot should always enforce:

```text
effective_at <= t
```

Knowledge-time snapshot should enforce:

```text
effective_at <= t
AND
observed_at <= t
```

Use:

```python
if o.effective_at > at:
    continue

if mode == "knowledge" and o.observed_at > at:
    continue
```

This is a real temporal bug.

Add regression test.

---

# POWK P0.3 — remove coefficients from Edge

The spec says all time-varying properties are Observations, but Edge still carries:

```text
coefficient
coefficient_unit
```

A physical coefficient can change with:

```text
technology
efficiency
engineering practice
process
geography
```

Move it to edge-targeted Observation:

```text
subject = edge_id
metric = requirement_coefficient
value = 4.2
unit = worker_hour/MW
```

Then Edge becomes exactly:

```text
id
source
target
relation
valid_from
valid_to
observed_at
```

This is cleaner.

---

# POWK P0.4 — adapters are currently violating REQUIRES semantics

This is the biggest issue in current Layer-1 integration.

The repair adapter currently creates things conceptually like:

```text
brand REQUIRES category
category REQUIRES fault
```

Those are not dependency constraints.

A brand does not require a product category in the POW sense.

A product category does not require a fault.

The code comments even acknowledge:

> this is a simplification.

Do not do this.

The kernel graph must not be populated merely because two entities have a relationship.

Remember:

```text
A REQUIRES B
=
A cannot scale / function / occur without B
```

If we pollute REQUIRES with:

```text
made_by
belongs_to
has_fault
contains
```

the kernel becomes meaningless.

---

# Repair adapter should initially export almost no edges

That is fine.

Layer 1 can export observations without a dependency edge.

Example:

```text
Node:
repair:category:washing_machine

Observation:
failure_rate
repair_success_rate
median_age
parts_availability
used_price
```

Only create a dependency when we have actual evidence such as:

```text
repair_action
REQUIRES
replacement_part

repair_action
REQUIRES
technician_skill
```

or:

```text
asset_function
REQUIRES
component
```

Unknown graph is better than false graph.

---

# Same discipline for PowPowPow

This relation can be valid:

```text
Monero mining
REQUIRES
CPU compute
```

But:

```text
coin network
REQUIRES
hardware
```

may be too vague depending on what the Node actually means.

Define nodes precisely.

For example:

```text
powpowpow:activity:xmr_mining
REQUIRES
powpowpow:capability:randomx_compute
```

is cleaner than:

```text
XMR Network
REQUIRES
Ryzen 7950X
```

because XMR does not require that particular model.

The adapter needs to avoid accidental over-specificity.

---

# POWK adapter rule

Before emitting any edge ask:

> If B disappeared, would A's ability to operate/scale materially fail?

If no:

```text
DO NOT EMIT REQUIRES
```

---

# POWK adapters currently hard-code paths

Current code contains paths like:

```text
/home/ubuntu/powpowpow
/home/ubuntu/repair
/home/ubuntu/powk/exports
```

Replace with CLI/env configuration.

Example:

```bash
pow-adapt repair \
  --source /srv/pow/repos/repair \
  --out /srv/pow/state/exports/repair
```

or env:

```text
POW_ROOT
POWK_EXPORT_DIR
```

Adapters need to be reproducible on another machine.

---

# Where adapters should live

There is a subtle architectural question.

Current:

```text
powk/adapters/
```

works for prototyping.

Long term, I would move adapters into each garden:

```text
powuk/export_pow.py
repair/export_pow.py
powstock/export_pow.py
powpowpow/export_pow.py
```

Why?

The garden understands its own schema.

POWK should not know:

```text
repair SQLite table names
powpowpow JSON file locations
```

Correct dependency:

```text
garden knows how to export itself
POWK knows how to ingest canonical records
```

Not:

```text
POWK knows every garden's database internals.
```

During this development phase, existing adapters can stay where they are until their contracts settle.

But don't add 15 more adapters inside POWK.

---

# Repair effective time is currently fabricated

Current repair adapter gives aggregate observations an effective time roughly like:

```text
2026-01-01
```

with a comment equivalent to:

> dataset covers all time.

That is not valid temporal semantics.

If an aggregate contains records spanning years, it does not mean:

```text
the aggregate was true on Jan 1 2026.
```

This is exactly how backtests acquire hidden leakage.

Instead either:

```text
A. derive historical time buckets from the actual repair dates
```

or:

```text
B. expose the aggregate as observed_at only and clearly mark effective interval
```

Prefer A.

The whole reason for POWK is historical state.

Do not destroy chronology during adapters.

---

# PowPowPow adapter also needs careful observed_at handling

Current adapter uses:

```text
observed_at = export time
```

even though PowPowPow may already have original collection timestamps.

Use the original ingestion/observation timestamp whenever available.

Adapter execution time should be:

```text
exported_at
```

if retained at all.

Do not replace:

```text
when we learned the fact
```

with:

```text
when we happened to run the adapter.
```

That would make knowledge-time backtests incorrect.

---

# Evidence generation needs stronger provenance

Current adapters synthesize claims like:

```text
"Chain state observation ..."
```

with:

```text
publisher=powpowpow
```

But PowPowPow itself may have obtained it from:

```text
Qubic RPC
Monero node
CoinEx
etc.
```

Evidence should preserve the original source.

Example:

```text
publisher = Qubic RPC
source_uri = rpc.qubic...
lineage_root = raw artifact hash
content_hash = raw payload SHA256
```

PowPowPow is the collector, not necessarily the publisher.

Same for Repair/Open Repair.

This matters later when weighting evidence.

---

# Layer-1 export contract

Each garden should eventually emit a bundle:

```text
manifest.json
nodes.jsonl
edges.jsonl
observations.jsonl
evidence.jsonl
```

Manifest:

```json
{
  "protocol": "pow/0.2",
  "garden": "powuk",

  "exported_at": "...",

  "source_revision": "git:...",

  "counts": {
    "nodes": 1242,
    "edges": 315,
    "observations": 182913,
    "evidence": 182913
  },

  "files": {
    "nodes.jsonl": "sha256:...",
    "edges.jsonl": "sha256:...",
    "observations.jsonl": "sha256:...",
    "evidence.jsonl": "sha256:..."
  }
}
```

POWK verifies hashes before ingestion.

---

# Do not overwrite exports

Current adapters use:

```text
nodes.jsonl
observations.jsonl
```

and rewrite them.

For reproducibility, prefer versioned export bundles:

```text
exports/
  repair/
    2026-09-22T05-00-00Z/
```

or content-addressed bundle IDs.

Then we know exactly which Layer-1 export fed a model run.

---

# POWK model hash

The latest fix is much better.

`hash_file()` now hashes exact bytes.

Good.

However, avoid fallback model hashing in production execution.

Current fallback eventually hashes:

```text
class name
```

if source cannot be found.

That violates the strong reproducibility claim.

For proper model execution:

```text
no source hash
→ reject model
```

Use fallback only in tests/dev if absolutely necessary.

Production runner should require verified model artifact hash.

---

# Full hash, not 16-character hash

Current code truncates SHA-256 to 16 hex characters.

That's fine for display.

Do not use the truncated hash as the authoritative identity if we are serious about content addressing.

Store:

```text
full 64 hex SHA256
```

Display:

```text
first 12–16 chars
```

Same principle for content IDs where practical.

---

# DERIVATION determinism

Very good design:

```text
ID does not depend on output value.
```

Keep this.

Then:

```text
same model
same snapshot
same inputs

but different result
```

creates a collision and exposes nondeterminism.

That's powerful.

Add an explicit test where a deliberately nondeterministic model is run twice and fails verification.

---

# Snapshot identity

Add a content-addressed snapshot ID.

A snapshot should have:

```text
snapshot_id
at
mode
input_bundle_hashes
```

Possible identity:

```text
SHA256(
    mode
    at
    sorted node IDs
    sorted edge IDs
    sorted selected observation IDs
    sorted selected evidence IDs
)
```

Then model runs can state:

```text
snapshot_id = ...
model_hash = ...
```

This makes every experiment reproducible.

---

# Model run receipt

Add a small `RunReceipt` outside the five canonical economic objects.

Operational metadata, not graph ontology.

Example:

```json
{
  "run_id": "run:...",
  "snapshot_id": "...",

  "model": "pressure/1.0.0",
  "model_hash": "...",

  "started_at": "...",
  "finished_at": "...",

  "derivation_ids": [...],

  "status": "ok"
}
```

This is useful for backtesting infrastructure later.

Do not make it a NODE.

---

# build_snapshot.py needs shrinking

Current adapter `build_snapshot.py`:

```text
loads exports
merges graphs
prints graph
computes unknowns
runs pressure model
```

The first two are infrastructure.

The latter two are research/example behavior.

Split:

```text
powk ingest
powk snapshot
```

from:

```text
examples/run_pressure.py
```

Kernel infrastructure should not automatically invoke a pressure model.

---

# Future POWK MCP

Eventually, yes, give Pi a separate Layer-2 MCP server.

But do NOT put it in POWOps.

Architecture:

```text
Pi

├── powops MCP
│      operational reality
│
└── powk MCP
       analytical historical state
```

POWK MCP should initially be read-only.

Potential tools:

```text
powk_snapshot
powk_node
powk_dependencies
powk_path
powk_observations
powk_evidence
powk_unknowns
powk_run_model
powk_compare_snapshots
```

Then Pi could ask:

```text
"Why are you interested in UK transformer data?"

POWK:
datacentre → grid connection → transformer

Unknown:
UK transformer capacity
lead-time history
```

And Pi can tell you:

> "The current dependency graph says transformer capacity is a major unknown between UK data-centre growth and grid expansion. There is no Layer-1 historical lead-time series yet. That looks like a garden gap."

That is exactly where this architecture becomes powerful.

---

# Keep POWK MCP read-only initially

`powk_run_model` is conceptually safe because it derives data.

Do not expose:

```text
edit graph
write node
invent edge
modify evidence
```

through the first MCP.

New graph facts must originate through controlled adapters/import.

---

# Pi should never hallucinate missing graph edges into canonical data

Important rule:

```text
LLM hypothesis
≠
POWK fact
```

Pi may propose:

```text
"Data centres probably require X"
```

but that stays a hypothesis until supported and imported properly.

If Pi discovers a candidate edge, create:

```text
candidate/
```

or research output.

Do not insert directly into canonical graph.

---

# AGENT MONITORING DESIGN

The eventual system I would aim for:

```text
                       YOU
                        ▲
                        │
                  PI / HARNESS
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     POWOPS MCP      POWK MCP     communication
          │             │
          ▼             ▼
     operations       analysis
          │             │
          └──────┬──────┘
                 ▼
           recommendations
```

Pi could handle:

```text
"Tell me only when a garden breaks."

"Every morning tell me:
- collectors that failed
- important schema changes
- missing priority sources
- new POWK unknowns"

"Watch POWUK and tell me if the training datasets stop updating."

"Run the transformer constraint model weekly and tell me when
new Layer-1 data would materially improve it."
```

That is exactly the end state.

---

# But notifications must be agent-level

Do not implement:

```text
powops.telegram.py
powops.chat.py
powops.email_agent.py
```

unless needed solely as generic alert transports.

POWOps emits incidents/events.

Pi decides:

```text
whether this merits bothering you
how to explain it
what action to propose
```

---

# Dashboard should eventually show Pi activity

A small additional view later:

```text
AGENT
```

but not a chatbot UI.

Show:

```text
last agent check
open incidents seen
actions proposed
actions executed
last action receipt
```

This helps audit autonomous behavior.

Example:

```text
05:20  Pi inspected NESO incident
05:22  proposed restart
05:24  approved by user
05:24  collector restarted
05:27  successful collection verified
05:27  incident closed
```

Excellent operational visibility.

---

# POWOPS action safety

For future autonomy implement capability tiers:

```text
TIER 0
read only

TIER 1
safe collector operations
run/restart

TIER 2
backup and restore-test

TIER 3
deployment/config changes

TIER 4
arbitrary shell
NEVER expose through standard MCP
```

Pi starts at Tier 0.

Then perhaps Tier 1.

Do not jump further.

---

# Systemd review

Current systemd files still hard-code:

```text
/home/ubuntu/powops
/usr/bin/python3
```

Fix.

Use installed venv:

```text
/srv/pow/venvs/powops/bin/python
```

or:

```text
%h/...
```

where appropriate.

Also current user service writes:

```text
/var/log/powops-health.log
```

A user systemd service may not have permission.

Use journald:

```text
StandardOutput=journal
StandardError=journal
```

POWOps already has operational history; duplicate file logging is unnecessary.

---

# Add systemd hardening

For dashboard service:

```text
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
```

with explicit write path for:

```text
POWOPS_STATE_DIR
```

Keep network access as needed.

Don't overcomplicate, but basic sandboxing is appropriate for an exposed admin service.

---

# POWOPS tests to add

Current 68 tests are a good start.

Add:

```text
dashboard auth
dashboard unauthenticated rejection
dashboard API bounds
dashboard security headers

MCP initialization
MCP list tools
MCP invoke status

health last_attempt vs last_success
incident open
incident update
incident recovery
event stream

garden-manifest discovery
manifest merge/conflict

backup receipt
backup verification
```

---

# POWK tests to add now

In addition to existing 57:

```text
future effective_at cannot appear in world snapshot
future effective_at cannot appear in knowledge snapshot

edge observed_at anti-lookahead
node observed_at anti-lookahead

adapter cannot emit invalid relation types
adapter preserves source observation timestamp

same snapshot generates same snapshot_id

full model hash stable
model source byte change changes hash

false REQUIRES fixture rejected by semantic adapter tests
```

The semantic edge tests belong in adapters, not kernel.

---

# Priority development order

Do not work randomly.

## Pass 1 — security

```text
1. rotate dashboard token
2. remove secret from README
3. deploy Cloudflare Access
4. stop query-token auth for remote access
5. add security headers
6. stop logging token
```

---

## Pass 2 — POWK remaining temporal correctness

```text
7. add observed_at to Node/Edge
8. fix effective_at snapshot condition
9. add structural anti-lookahead tests
10. remove Edge coefficient fields
11. full SHA256 model identity
12. add snapshot_id
```

---

## Pass 3 — adapter correctness

```text
13. remove fake repair REQUIRES edges
14. review every PowPowPow edge semantically
15. preserve actual source timestamps
16. remove fabricated repair effective date
17. improve evidence provenance
18. remove hard-coded filesystem paths
19. add export bundle manifest/hashes
20. make exports versioned/immutable
```

---

## Pass 4 — POWOps operational contract

```text
21. garden-owned source manifests
22. health artifact v1
23. last_attempt / last_success
24. coverage model
25. backup receipts and verification
26. incident model
27. event stream
```

---

## Pass 5 — dashboard

```text
28. STATUS
29. COVERAGE
30. INCIDENTS
31. VOLUME
32. SCHEMAS
33. BACKUPS
34. source drill-down
```

No charts unless a chart genuinely conveys useful temporal information.

---

## Pass 6 — MCP

```text
35. pin MCP SDK
36. add integration handshake test
37. structured tool outputs
38. add incidents
39. add coverage
40. add backup state
41. add logs
42. add event feed
```

Remain read-only.

---

## Pass 7 — safe autonomy later

After monitoring has been stable:

```text
43. typed run_source action
44. typed restart_source action
45. action allowlist
46. action receipts
47. verified recovery
48. Pi harness integration
```

Stop there before allowing broader control.

---

# Definition of done for POWOPS v0.2

POWOps is done when:

```text
all active Layer-1 sources discoverable
garden-owned manifests supported
health artifacts standardized
health ≠ coverage
incidents durable
events append-only
backups visible and verified
dashboard securely accessible
MCP read-only API complete
tests cover dashboard + MCP
no economics anywhere
```

---

# Definition of done for POWK v0.2

POWK is done when:

```text
Node/Edge/Observation/Evidence temporal semantics correct
no future-information leakage
records content-addressed
full model hashes
snapshot IDs reproducible
counterfactuals immutable
adapters preserve chronology
false dependency edges removed
all four gardens can eventually export canonical bundles
kernel contains zero domain assumptions
model execution is reproducible
```

Then stop changing the kernel casually.

---

# The key architecture after this pass

```text
                         POW SYSTEM

                         REALITY
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
    POWUK                REPAIR              POWPOWPOW
       │                    │                    │
       └─────────────┬──────┴──────────┬─────────┘
                     │                 │
                     ▼                 ▼
                  Layer 1           POWSTOCK
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
       POWOPS               CANONICAL EXPORTS
          │                     │
    health/incidents             ▼
    backups/events              POWK
    MCP/dashboard           snapshots/replay
          │                     │
          ▼                     ▼
       Pi MCP               models/research
          │                     │
          └──────────┬──────────┘
                     ▼
                   PI AGENT
                     │
                     ▼
                    USER
```

The important insight is that the Pi agent should sit **above** POWOps and POWK.

It should not become part of either.

POWOps tells Pi:

> What is operationally true?

POWK tells Pi:

> What does the historical empirical substrate contain?

Models tell Pi:

> What do particular hypotheses infer?

Pi tells the user:

> What matters right now, why, and what action is available?

That is a very strong architecture.

---

# Absolute scope guards

For POWOps:

> If it does not improve our ability to know whether Layer-1 collection/history is healthy, it does not belong.

For POWK:

> If it does not improve deterministic reconstruction, traversal, replay or model execution over dependency state, it does not belong.

For Pi:

> Interpretation, prioritization, conversation and controlled action belong here.

Keep these three boundaries hard.

That is the cleanest path from the current data gardens to an eventual autonomous economic observatory without rebuilding another Killfeed.

The latest work is materially better than the previous revision. The biggest remaining risks are no longer "missing features"; they are **security, temporal leakage, false dependency edges, and allowing the operator/agent surfaces to absorb domain logic**. Fix those four classes before expanding Layer 2 modelling.
