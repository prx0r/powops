# POW Development Plan

**The northstar document.** Every repo references this. Read goldmoat.md, goldmoat2.md and powvision.md for full reasoning.

---

## The thesis in one sentence

POW is the procurement and compatibility intelligence layer for physical robotics — it knows what parts robots need, how to obtain them, and learns from every transaction.

---

## The flywheel

```
PROCUREMENT GRAPH
  robot → revision → BOM → parts → suppliers → UK cost
          ↓
PRODUCTS (spare parts, kits, consumer agents)
  sold to repairers, builders, hobbyists
          ↓
OUTCOME DATA (the moat)
  what actually failed, what worked, what shipped on time
          ↓
FEEDS BACK INTO GRAPH
  more accurate, more reliable, more useful
```

---

## Repository map

| Repo | Job | Builds toward |
|------|-----|---------------|
| **powops** | Monitor everything, expose status, coordinate the system | Mission control |
| **powrobots** | Robot models, revisions, BOMs, manufacturer docs | Robot-to-parts graph |
| **powproducts** | Canonical part identity, exact specs, verified compatibility | Parts intelligence |
| **powphysical** | Supplier offers, prices, landed costs, fabrication quotes | Procurement engine |
| **repair** | Faults, repair procedures, replacement outcomes, economics | Outcome data |
| **powuk** | UK opportunities, training, trades, procurement notices | Market demand |
| **powk** | Shared data contracts, historical transformations | Infrastructure |

---

## Three phases

### Phase 1: Spare parts (months 1-3)

**Goal:** Prove that verified spare-parts procurement with UK-held stock generates repeat business.

**powrobots:** Register 10 robot vacuum models + 2-3 open-source arms (SO-101). Document exact models, revisions, BOMs. Start with Dreame L10s Ultra, Roborock S7, iRobot Roomba.

**powproducts:** Build canonical part registry. Map manufacturer part numbers to exact components. Three substitution types: verified drop-in, compatible-with-modifications, candidate-only.

**powphysical:** Integrate LCSC for electronic components. Build landed-cost model (VAT, duty, shipping). First 5 parts with 2+ supplier quotes each. UK dispatch time tracking.

**repair:** Document repair procedures from iFixit and manufacturer manuals. Record which parts actually fail. First 5 repair outcome records.

**powops:** Monitor all collectors. Dashboard shows which gardens are collecting, which aren't. 55 sources now, need health verification.

**First commercial milestone:** 10 paid spare-parts orders from UK repair technicians. Verify: Dreame dock pump (`20020100005232`), Dreame solenoid (`20020100009618`), Roborock charging contacts (`9.01.0248`), Roborock S7 LiDAR motor.

### Phase 2: Kits and procurement API (months 3-6)

**Goal:** A customer selects a supported robot design and gets an executable UK-delivered purchasing basket.

**powrobots:** Expand to 30+ robot models. Add robotic lawnmowers (Husqvarna, Gardena). Document LeRobot SO-101 complete BOM with exact gear ratios per joint.

**powproducts:** 200+ verified parts. Cross-model compatibility graph. First custom PCB candidates from repeated configurations.

**powphysical:** JLCPCB integration for fabrication quotes. Two basket modes: fastest delivery vs. lowest cost. MCP endpoint for AI assistants.

**repair:** 50+ repair outcomes. Failure-rate data by component and supplier. Supplier reliability scores from actual orders.

**powuk:** First 5 UK repair businesses onboarded. Match parts requests to inventory. Training pathway data for robotics technicians.

**First commercial milestone:** SO-101 complete build kit available. Customer gets verified BOM + UK-delivered quote in one checkout. 50 kits sold.

### Phase 3: Manufacturing API and consumer products (months 6-12)

**Goal:** Any AI application can source and eventually commission the manufacture of a physical robot.

**powrobots:** 100+ robots. Full BOM coverage for supported designs. New model detection from manufacturer announcements.

**powproducts:** 1000+ parts. Automated substitution detection. Compatibility confidence scores from accumulated evidence.

**powphysical:** Full procurement API: `resolve_bom`, `find_substitutes`, `optimize_bom`, `quote_build`, `create_order`. Assembly partner network.

**repair:** 200+ outcomes. Predictive failure models. Warranty claim patterns.

**POW consumer products:** ESP32 Agent Node platform. Plant agent, desk agent, pet agent. Custom PCB from Phase 2 learnings. Etsy + direct sales.

**First commercial milestone:** AI assistant successfully requests, modifies and obtains a complete quote for a supported design through MCP. 500 units sold across product lines.

---

## Checkpoints

### Checkpoint 0: Baseline (done)
- [x] All 9 repos inventoried
- [x] VPS runtime state verified
- [x] Security findings documented
- [x] 55 sources in sources.yaml
- [x] Health correctness fixes applied

### Checkpoint 1: Collecting
- [ ] All 7 gardens discovered from owner-controlled manifests
- [ ] Every collector produces a run receipt
- [ ] Dashboard shows real collection status, not config status
- [ ] No false-green health signals

### Checkpoint 2: Verified data
- [ ] 10 robot models with exact BOMs in powrobots
- [ ] 50 parts with verified compatibility in powproducts
- [ ] 5 parts with UK landed costs from actual quotes in powphysical
- [ ] 5 repair outcomes recorded in repair

### Checkpoint 3: First transaction
- [ ] 10 paid spare-parts orders from real customers
- [ ] Actual delivery times tracked against quotes
- [ ] Supplier performance data from real orders
- [ ] Outcome data feeding back into graph

### Checkpoint 4: Kits available
- [ ] SO-101 build kit with verified BOM and UK-delivered quote
- [ ] 50 kits sold
- [ ] Two basket modes working (fastest vs. cheapest)
- [ ] MCP endpoint for AI assistants operational

### Checkpoint 5: API live
- [ ] `resolve_bom`, `find_substitutes`, `optimize_bom` endpoints working
- [ ] AI assistant successfully obtains a complete quote
- [ ] 500 units sold across product lines
- [ ] Custom PCB from accumulated configuration data

### Checkpoint 6: Manufacturing
- [ ] `quote_build` and `create_order` endpoints working
- [ ] Assembly partner network established
- [ ] First fully assembled robot delivered
- [ ] Consumer product line generating outcome data

---

## What each repo should build next

### powrobots
Register the Dreame L10s Ultra, Roborock S7 and SO-101 with exact revisions, gear ratios, motor configs and BOMs. This is the foundation — nothing else works without knowing exactly which robot and which revision.

### powproducts
Build the canonical part registry. One manufacturer part number = one entity. No duplicate identities. Track three substitution levels. Start with the Dreame dock components and Roborock LiDAR parts.

### powphysical
Integrate LCSC API. Build the landed-cost calculator (price + shipping + duty + VAT). Track UK dispatch times from actual supplier observations. First 5 parts with 2+ quotes.

### repair
Document the SO-101 repair procedures. Map which components fail and why. First 5 repair outcomes with actual parts, costs and times.

### powops
Fix the remaining health gaps. Add the 3 new gardens to monitoring. Dashboard needs overview, gardens and development views. MCP needs `powops_diagnose`.

### powuk
Identify first 5 UK repair businesses. Map robotic mower servicing opportunities. Connect to training providers.

### powk
Define shared data contracts. One part identity, one compatibility predicate, one observation schema. All repos must use these.

---

## The hard constraints

1. **Verified compatibility only.** Never claim a part works without evidence. Three levels: drop-in, needs-modification, candidate-only.
2. **Transaction outcomes are the moat.** Every order teaches something the graph can't learn from scraping.
3. **UK-held stock for fast-movers.** China for sourcing, UK for fulfillment on time-sensitive parts.
4. **One canonical part identity.** No duplicate registries across repos.
5. **Safety-critical parts need functional testing.** Cliff sensors, LiDAR, charging — dimensional matching isn't enough.
6. **Lithium batteries are a separate problem.** Require UN38.3 certs, defer until demand proven.
7. **Don't become an electronics distributor.** RS/Farnell/Mouser already won that. Be the robotics-specific intelligence layer.
8. **The AI manufacturing API is the payoff, not the starting point.** Build the graph and transact first.

---

## Source vision docs

| Document | What it covers |
|----------|---------------|
| `goldmoat.md` | The flywheel: graph + product + outcome data |
| `goldmoat2.md` | Spare parts as first transaction + vibecoding backend |
| `powvision.md` | Core thesis and repository responsibilities |
| `robotprintify.md` | Consumer physical agent products |
| `commercial2.md` | Business model and revenue streams |
| `shopifygoat.md` | E-commerce intelligence research |
| `commercial.md` | 20 commercial product ideas |
| `roadmap.md` | Mission control development phases |
| `nextsteps.md` | Robot parts intelligence focus |
| `ministar.md` | Immediate priorities |
