# POW System Architecture Overview

> NOTE (2026-09-23): historical design document. Predates the 7-garden
> registry (powproducts, powrobots, powphysical added later), the incident/
> event subsystems, and the MCP server. Architecture direction still valid;
> specifics (e.g. "29 sources", "four gardens", file layouts) are stale.
> See README.md, AUDIT.md and vision/devplan.md for current state.

Yes. After reviewing the actual four repos, I think your revised three-layer picture is **cleaner than the architecture I was pushing earlier**, and I would keep the Layer-1 gardens as separate repositories.

One correction: the stock repo is currently `prx0r/powstock`, singular, not `powstocks`.

The reason separation works is that these aren't arbitrary divisions. Each has a coherent collection boundary:

```text
LAYER 1 — OBSERVE REALITY

powpowpow
    compute / PoW / crypto-resource telemetry

powuk
    UK physical capacity / labour / infrastructure / policy

powstock
    UK public-market / corporate / ownership / microstructure telemetry

repair
    physical asset / failure / parts / resale / intervention telemetry
```

That is a good decomposition. I would **not merge them**.

What needs changing is what we expect those repos to do.

---

## The architecture I'd lock in

```text
                         POW.SYSTEMS
                              │
                              │
                  ┌───────────┴───────────┐
                  │                       │
              REAL WORLD              HISTORY
                  │                       │
                  ▼                       ▼
════════════════════════ LAYER 1 ════════════════════════

     powpowpow     powuk      powstock      repair
         │           │           │            │
         │ collectors / raw data / source-native parsing
         │ provenance / backfills / continuous snapshots
         │
         └───────────────┬───────────────────┘
                         │
                   RAW DATA LAKE
                         │
                         ▼
════════════════════════ LAYER 2 ════════════════════════

                 NORMALISE + MODEL
                         │
             identity / joins / units
             temporal alignment
             feature engineering
             graph construction
             causal discovery
             ML
             backtests
             counterfactuals
             dependency modelling
                         │
                         ▼
                 EMPIRICAL STATE
                         │
                         ▼
════════════════════════ LAYER 3 ════════════════════════

                   ECONOMIC THEORY
                         │
            constraints / shadow prices
            Seesaw / bottleneck migration
            assimilation latency
            AGI impact models
            intervention response
            value capture
            future-world divergence
                         │
                         ▼
                 RESEARCH / DECISIONS
```

This is substantially cleaner.

---

## Layer 1 should be boring

This is the biggest architectural rule.

Layer 1 should become almost obsessively boring.

Its job is:

> **Capture reality faithfully enough that future versions of us can ask questions we haven't thought of yet.**

That means Layer 1 should care about:

```text
source discovery
collection
backfill
raw preservation
timestamps
source versioning
deduplication
integrity hashes
schema-drift detection
collector health
licensing
provenance
coverage
```

It should **not care whether Seesaw is true**.

It should not even particularly care what model we intend to use next month.

That is how you avoid contaminating your garden with today's thesis.

---

## Your existing repos are already telling us this

### `powpowpow`

This is currently the most mature project, but it has all three layers mixed together.

The README describes real Layer-1 infrastructure:

```text
REST L2 collectors
WebSocket tick archive
chain pollers
QUBIC computor snapshots
raw append-only storage
Parquet archival
daily snapshots
```

That is excellent Layer 1.

But the same repo also contains things like:

```text
02_pressure_equation_research.md
03_seesaw_filter.md
backtest.py
analytics scripts
derived metrics
```

Those are Layer 2/3.

The original architecture document literally says:

```text
official chain/node
→ immutable raw events
→ normalized chain tables
→ SafeTrade L2/trades
→ derived metrics
→ backtests/API/content
```

So `powpowpow` already discovered your three layers internally. We just hadn't generalized that structure across POW.

I would treat it as the **reference implementation** for Layer 1 operational discipline.

---

### `powuk`

This repo is also currently crossing the boundary.

The collector side is Layer 1:

```text
certification registers
apprenticeships
training providers
jobs
Companies House
planning
procurement
grid
legislation
```

Excellent.

But:

```text
compiler/scarcity.py
models/
pow_scarcity_daily
capacity_response_ratio
severity scores
opportunities
```

are already Layer 2 or Layer 3.

That's why POWUK started feeling broad and slightly confusing.

It's trying to be both:

```text
UK OBSERVATORY
```

and

```text
UK CONSTRAINT MODEL
```

Those should be separate conceptual layers.

POWUK becomes much easier to understand when its mission is simply:

> **Continuously preserve the observable state of UK physical economic capacity and demand.**

No need for it to decide what constitutes a binding constraint.

---

### `powstock`

This is perhaps the clearest example.

The Layer-1 data garden is excellent:

```text
prices
L2 order books
trades
RNS
director transactions
ownership
Companies House accounts
corporate actions
production disclosures
```

But the README currently says it imports:

```text
fish strategy engine
ensemble
backtest
constraint model
physical-reasoning compiler
```

That is exactly the sort of dependency I'd now remove **conceptually**.

Powstock should not need Fish.

Powstock should not need POWUK's scarcity model.

Powstock's job is to preserve the market/corporate tape.

Then Layer 2 can ask:

```text
does UK grid constraint state predict
LSE electrical-equipment repricing?
```

That distinction is important because otherwise you're baking the target model into the sensor.

---

### `repair`

Repair is actually moving in the right direction already.

Its latest `AGENTS.md` is much better than the older README.

It now describes five gardens:

```text
ASSET
FAILURE
PARTS
MARKET
OUTCOME
```

and reports actual evidence such as:

```text
305,649 Open Repair records
idempotent raw storage
SHA256 blobs
derivation pipeline
```

That's strong.

But:

```text
RepairEconomics
fix/replace verdict
margin models
powlab
pow_research
experiments
```

are Layer 2/3 concerns.

Layer 1 Repair should just preserve:

```text
what object?
what failed?
what component?
what intervention?
what did it cost?
what happened afterwards?
what was it worth?
```

That dataset becomes vastly more valuable than today's repair-margin formula.

---

## So yes: keep the repos separate

I would absolutely keep:

```text
/prx0r/powpowpow
/prx0r/powuk
/prx0r/powstock
/prx0r/repair
```

Separate repos give you:

* independent collector failures;
* clear source ownership;
* easier debugging;
* independent deployment cadence;
* manageable agent context;
* domain-specific tests;
* no mega-repo contamination.

And, importantly, **a coding agent working on NESO does not need to understand Monero RPC or eBay listings.**

That's exactly the sort of context containment we want.

The shared layer should be operational contracts, not a shared codebase.

---

## One VPS is also exactly what I'd do initially

Something like:

```text
/srv/pow/
├── repos/
│   ├── powpowpow/
│   ├── powuk/
│   ├── powstock/
│   └── repair/
│
├── data/
│   ├── powpowpow/
│   ├── powuk/
│   ├── powstock/
│   └── repair/
│
├── logs/
│
└── state/
```

Each repo gets its own venv:

```text
/opt/venvs/powpowpow
/opt/venvs/powuk
/opt/venvs/powstock
/opt/venvs/repair
```

And its own systemd units.

Not Docker-compose theatre unless we actually need it.

---

## But standardize Layer 1 operationally

This is the thing I'd enforce across all four.

Every source should have a manifest roughly equivalent to:

```yaml
id: neso_connection_queue
garden: powuk

source:
  authority: NESO
  type: csv
  url: ...

collection:
  cadence: daily
  backfill_from: 2018-01-01

storage:
  raw: true
  append_only: true

time:
  source_timestamp: true
  observed_at: true

health:
  expected_min_rows: 100
  max_staleness_hours: 48

license:
  redistribution: allowed
```

Then every collector exposes the same basic health state:

```text
last_attempt
last_success
records_seen
records_new
bytes
source_timestamp
schema_hash
error
```

**This is probably more important right now than agreeing on a universal economic schema.**

---

## I would create one tiny operational repo

Not POWKernel yet.

Something more like:

```text
powops/
```

But keep it very small.

Its purpose:

> Run and monitor Layer 1.

It contains no economics.

```text
powops/
├── sources.yaml
├── health.py
├── status.py
├── backup.py
├── deploy/
│   └── systemd/
└── tests/
```

Then:

```bash
pow status
```

could show:

```text
SOURCE                         LAST GOOD       AGE      ROWS      STATUS

Qubic RPC                      00:29           4m       1,830     ✓
XMR daemon                     00:28           5m       283       ✓
NESO queue                     23:05           1h28     12,493    ✓
Companies House stream         00:30           3m       49        ✓
Open Repair                    21 Sep          27h      305,649   ✓
LSE RNS                        00:27           6m       13        ✓
IBKR L2                        —               —        —         BLOCKED
```

That is the Layer-1 command centre.

No scoring.

No AGI thesis.

No graph engine.

Just: **are the gardens alive?**

---

## Raw storage should also be shared physically

This part of your "same server" idea is particularly good.

The repositories remain separate, but they don't each need to invent storage.

Something like:

```text
/data/pow/raw/
    powuk/
    powstock/
    repair/
    powpowpow/
```

with eventual replication to R2.

Then:

```text
RAW on VPS
    ↓
scheduled upload
    ↓
R2 immutable archive
```

And analytical Parquet locally/R2 as necessary.

You can eventually lose the VPS and rebuild Layer 2 from the historical raw archive.

That's the resilience test.

---

## Layer 2 is where normalization belongs

This is where I'd now put what we were calling POWKernel.

But I would broaden the notion slightly.

Layer 2's purpose is:

> **Turn heterogeneous observations into comparable empirical state.**

This includes:

```text
entity resolution
units
time alignment
geography alignment
classification
feature construction
dependency edges
installed-stock estimates
BOM coefficients
capacity estimates
lead-time series
price indices
failure hazards
market state
```

And importantly:

```text
ML
causal inference
backtests
```

This is where your empirical discipline lives.

---

## I'd split Layer 2 into two conceptual halves

Not necessarily repos yet.

```text
L2A — NORMALIZATION

raw → comparable state


L2B — EMPIRICAL MODELS

comparable state → tested relationships
```

For example:

```text
L1:
17,583 individual UK vacancy records

L2A:
electrician_vacancies(
    Manchester,
    2026-09-01
) = 231

L2B:
vacancy_growth leads wage_growth
by ~4 months
```

or:

```text
L1:
millions of L2 order-book updates

L2A:
daily depth / spread / replenishment

L2B:
supplier constraint shocks predict
liquidity withdrawal
```

That separation is very useful.

---

## This is where ML belongs

Absolutely.

Once Layer 1 becomes pristine historical data, Layer 2 can be aggressive experimentally.

We can test:

```text
gradient boosting
survival models
state-space models
change-point detection
Bayesian models
causal forests
Granger-style lead/lag
PCMCI
graph propagation
hazard models
diffusion models
representation learning
```

But none of those models get to mutate Layer 1.

That lets us throw them away freely.

This is an important psychological distinction:

> **Layer 1 is expensive historical truth. Layer 2 models are disposable hypotheses.**

---

## Backtesting should drive new Layer-1 collection

This is the really good feedback loop in what you're proposing.

Not:

```text
collect everything forever
```

but:

```text
L1 data
   ↓
L2 model
   ↓
backtest
   ↓
missing explanatory variable discovered
   ↓
NEW L1 SOURCE
   ↓
history starts accumulating
```

Example:

```text
Model:
transformer constraint predicts grid-project delays.

Backtest failure:
prediction disappears after controlling for
electrical-steel availability.

Question:
do we have steel capacity/inventory history?

No.

→ plant POWFlow source now.
```

That's exactly how the gardens should grow.

The scientific process determines what we plant next.

---

## Layer 3 should be allowed to be weird

This is where your frontier economics belongs.

Once Layer 1 and Layer 2 are solid, Layer 3 can contain:

```text
Seesaw
Free-Intelligence assumption
assimilation latency
constraint migration
shadow-price models
post-AGI worlds
economic topology
capital-response theory
Greer-style physical limits
Leontief propagation
technology diffusion
reflexive constraint relaxation
```

Now these aren't contaminating data collection.

We can test twenty theories against the same empirical substrate.

That's far healthier.

---

## And yes: AGI deserves a Layer-1 garden eventually

Your idea at the end is especially interesting.

I would **not make "POWAGI" an economic model first.**

I'd make an AI-capability observatory.

Something like:

```text
powai/
```

or:

```text
powagi/
```

Its Layer-1 job is to preserve changes in AI capability.

For example:

```text
model releases
benchmark results
benchmark saturation
inference cost
training cost
context length
latency
agent task duration
tool use
coding capability
robotics capability
scientific capability
multimodal capability
open-source weights
hardware requirements
API pricing
deployment volume proxies
```

And crucially:

```text
released_at
announced_at
benchmark_observed_at
price_change_at
deployment_available_at
```

Then Layer 2 can produce a **capability state vector**:

```text
AI(t) = {
    coding,
    reasoning,
    autonomy,
    robotics,
    science,
    inference_cost,
    multimodal,
    context,
    reliability,
    ...
}
```

---

## Then connect AI capability to the physical gardens

This gets extremely interesting.

```text
AI capability jump
      │
      ├─→ compute demand
      │      POWPOWPOW
      │
      ├─→ datacentre buildout
      │      POWUK
      │
      ├─→ grid connection pressure
      │      POWUK
      │
      ├─→ transformer / copper demand
      │      POWFlow
      │
      ├─→ robotics adoption
      │      Repair / physical assets
      │
      ├─→ labour displacement / shortages
      │      POWUK
      │
      └─→ listed-company repricing
             POWSTOCK
```

Then we can empirically ask:

> **What historically happens downstream when AI capability moves by X?**

rather than merely philosophizing about post-AGI.

That is potentially a very unusual dataset.

---

## The really powerful part is timestamps

Suppose we preserve:

```text
2026-09-04:
AI coding capability jumps

2026-09-07:
cloud inference demand rises

2026-09-19:
GPU rental rates move

2026-10-12:
datacentre announcements accelerate

2027-01:
grid applications increase

2027-03:
transformer lead times extend

2027-04:
electrical-equipment stocks reprice
```

Then we can actually estimate:

```text
AI capability
      ↓ Δt1
compute demand
      ↓ Δt2
physical capex
      ↓ Δt3
constraint
      ↓ Δt4
price
      ↓ Δt5
supply response
```

That is **Seesaw with empirical lag distributions**.

Much stronger than just writing down the Seesaw equation.

---

## So I would now define the system like this

```text
                    POW SYSTEM
                        │
                        ▼
              ═══ LAYER 1 ═══
                 OBSERVATORIES

    ┌──────────────┬──────────────┬───────────────┐
    │              │              │               │
 POWPOWPOW        POWUK         POWSTOCK        REPAIR
 compute        physical UK     capital         assets
 resources      economy         markets         lifecycle

                    + future

                    POWAI
                 AI capability

                    POWFLOW?
               physical supply
                 if required

                        │
                        ▼
              ═══ LAYER 2 ═══
              EMPIRICAL SCIENCE

               normalization
               entity linkage
               feature state
               dependency graph
               causal discovery
               ML
               backtests
               counterfactuals

                        │
                        ▼
              ═══ LAYER 3 ═══
               POW ECONOMICS

                  Seesaw
                shadow price
             bottleneck migration
            assimilation latency
               AGI impacts
              world divergence
              capital capture
```

I think that's much closer to the final architecture.

---

## What I would change **right now**

Don't rewrite the working collectors.

Instead, declare a phase change.

For all four repos:

```text
CHECKPOINT 1 = LAYER 1 COMPLETE
```

Success means:

```text
all priority sources collecting
historical backfill maximized
raw data immutable
source timestamps preserved
collector health visible
schema drift detectable
restarts safe/idempotent
R2 backup verified
licenses documented
coverage measured
```

**No requirement that scarcity models or trading signals work.**

That gives you a crisp finish line.

Then Layer 2 starts only when the gardens are reliably growing.

And I would make POWPowPow's storage/collection discipline the template, Repair's latest source-record/hash discipline the second template, and strip the **conceptual responsibility** for modelling out of all four Layer-1 repos—even if existing experimental code remains there temporarily.

That gives you the pristine foundation you're aiming for without another destructive rewrite.
