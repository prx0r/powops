# E-COMMERCE ALPHA DOSSIER
## Adam's ~$90k/day interview × Shopify public intelligence × the POW data-garden thesis
**Prepared 22 September 2026**
**Source discipline:** Interview claims are *self-reported*. External documentation is cited with direct official URLs. Proposed algorithms, forecasts and applications are *research hypotheses*, not facts about Adam's company.

---

## Executive thesis

The viral Shopify trick finds an apparent winner **today**. The enduring advantage comes from recording **how products, advertisements, prices, suppliers, reviews, inventory signals and commercial terms change over time**. Adam's interview provides a complementary lesson: a strong product can fail with exhausted advertising; substantial revenue can conceal operating losses; subscriptions can produce concentrated payment-processing risk; and moving closer to suppliers can improve cost, terms and new-product development. The actionable synthesis for POW is a historical, independently verifiable **product × creative × supplier × margin × operational risk graph**, not an AI landing-page factory.

**What this file contains:** transcript-derived evidence by timecode; validation of the Shopify/Meta tactics; a data-source directory; 20 research signals; practical unit-economics models; a creative-research workflow; a China/Asia supplier verification playbook; a POW L1–L4 architecture; full starter schemas; experiments and falsification criteria; build order; an agent-ready implementation brief; and source links.

### Five guardrails before using the research
1. `sort_by=best-selling` is a ranking based on the *all-time number of orders that contain a product*, not current sales volume, units sold, gross merchandise value, or profit. The website may override/disable sorting. [Shopify Help](https://help.shopify.com/en/manual/products/collections/collection-layout)
2. Public `/products.json` may expose prices, variants, titles, timestamps and availability, **if available**. It does **not** expose cost of goods, gross margin, customer identity, order history, or supplier invoice. Public endpoints vary by storefront; do not confuse them with authenticated `/admin/api/.../products.json`. [Shopify Ajax API](https://shopify.dev/docs/api/ajax), [Storefront API](https://shopify.dev/docs/api/storefront/2026-01)
3. For ordinary commercial ads, Meta's library generally reveals creative, date, advertiser, and platforms, but not spend, ROAS, CPA or profitability. Extra transparency exists for relevant UK/EU categories and political ads; access to historical commercial ads differs by region. [Meta Ad Library](https://www.facebook.com/ads/library/), [Meta Ad Library API](https://www.facebook.com/ads/library/api/)
4. A 60-day-old active ad is a **persistence signal**, not proof of return on ad spend. Neither an ad's endurance nor a copied landing page validates a product.
5. Only collect publicly accessible data within provider terms, robots rules and reasonable rates. Never circumvent access controls, personal-data restrictions, login gates, or anti-bot protections. Respect third-party copyright when saving or reproducing creatives. API coverage must be tested per provider.

---

# PART I — THE INTERVIEW, DISTILLED INTO TESTABLE BUSINESS MECHANISMS

## 1. Career chronology and quantitative claims

| Interview time | Self-reported observation | Research interpretation | What remains unknown |
|---|---|---|---|
| 1:35–3:35 | First sale after ~3 months, profitability after ~6 months and ~20 products; earlier winner later revived with different creatives | Creative and product performance are not equivalent | Spend, net profits, cohort sample sizes |
| 3:50–5:53 | ~$1m revenue month in November 2023; later months around **−$50k P&L** and cumulative six-figure debt; discontinued the brand after the following November underperformed | Successful top-line campaigns can hide structurally poor economics | Audited P&L, exact losses and debt |
| 5:55–6:52 | Tried roughly 10 supplements, found one with a distinctive, easy-to-explain mechanism; says users observed benefits | Differentiated product-story fit may lower explanation friction | Actual product, studies, attribution and causal efficacy |
| 8:08–8:41 | Current business doing **about $90k/day** | Gives scale for organizational discussion | Dates, revenue definition, profit, repeat rate, attribution |
| 14:20–16:48 | Spends roughly 8 hours/day, including ~1 hour business prioritization, 3–4 hours deep work, staffing and oversight | Priority clarity and resource allocation become a founder's job | Whether this routine is stable or transferable |
| 17:08–19:11 | At launch, 14–16-hour days heavily focused on creatives; mechanism explanation initially worked | Tight manual creative feedback loops can matter before organizational complexity | Number of ads and objective statistical lift |
| 19:36–20:43 | Moved toward more emotional/desire-based creative as competitors adopted similar mechanisms | Messaging must evolve as novelty decays | Whether this is causal or category-specific |
| 20:43–21:23 | ~150 creative batches/month; three strategists with three editors each | A recurring creative experiment-production operation | Definition of "batch", spend per batch, win rate |
| 25:18–26:48 | Hired substantially at ~$20k/day, delegated more at ~$50k/day; later adjusted because back-end issues were missed | Delegate a process only after feedback and management controls exist | Cost/size of each hire and whether thresholds generalize |
| 27:05–30:56 | Multiple China trips, direct supplier visits, pricing improvements and batch-testing discussion | Manufacturing capability and commercial terms are part of differentiation | Independent factory audit, agreement, actual savings |
| 31:06–32:21 | Reports payment-processing disruption and subscription revenue losses despite claimed 0.1% dispute rate | A single processor is a platform concentration risk | Processor reason, reserve terms, event chronology |
| 32:29–33:57 | Mostly uses Claude as augmentation; spent a month building AI automations later deemed useless; now hiring an AI specialist | Automate a measured constraint, not a fashionable technology | Automation baseline and opportunity cost |
| 33:57–34:24 | Targets ~$8m December and $10m January | Planning targets can coordinate procurement and ad spend | Not realized revenue |
| 34:56–37:15 | For brands at ~$250–400k/month, recommends reassessing product scalability, offer, creative, and new angles before AI/hiring | Reopen the causal hypothesis before adding operational complexity | Applicability to other businesses |

**Important inconsistency:** The auto-generated transcript has some transcription errors (including contradictory phrasing at ~4:56 and a likely mistranscribed "speed/dispute rate"). Do not silently treat every word as audited financial fact. Treat the figures as Adam's recollection.

## 2. The mechanism–message–market triangle

Adam reports that the first successful ads *explained an understandable product mechanism*; later, as the mechanism became less novel, his team expanded into emotional benefits and desires. Research consequence: maintain **two separate versioned entities**:

- **Product mechanism:** what physically or scientifically makes a product function; evidence level; novelty; competitor equivalence; regulatory constraints.
- **Message/angle:** who the buyer is; desired outcome; problem; level of awareness; frame; creative format; hook; call-to-action.

Never confuse a message's observed persistence with a mechanism's factual validity. In health products this distinction is legally material: FTC requires competent, reliable scientific evidence for applicable claims; GB supplement claims must comply with the authorised claims regime. Sources: [FTC Health Products Compliance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance), [ASA CAP section 15](https://www.asa.org.uk/type/non_broadcast/code_section/15.html).

### An example for POW's preferred physical-goods vertical
- **Mechanism:** modular replacement battery for a particular service robot, verified against actual electrical connector, voltage, dimensions, charger, safety spec.
- **Angles:** less downtime for cleaning contractor; field service without shipping the whole robot; affordable reuse for school robotics club; reduced inventory for robot repair technician.
- **Creative:** diagnostic teardown, timed repair demonstration, invoice comparison, technician testimonial with material-connection disclosure.
- **Falsifier:** advertised cost saving evaporates after shipping, failures, training or part incompatibility.

## 3. Creative strategy is product-market research

Adam's original product was revived with fresh creative after an apparent decline. Extract the principle **"ad failure does not identify the failed component"**. A falling ROAS could result from creative fatigue, offer deterioration, saturation, supply delays, landing-page friction, changed competition, price or measurement. Your database should track these independently. His structure (~3 strategists × 3 editors, ~150 batches/month) also implies that *the content pipeline itself can be instrumented*:

- Every hypothesis gets a unique ID, target audience, mechanism, angle, specific objection, creative variant, landing-page variant and launch date.
- Every experiment records impressions, clicks, CPC, CTR, landing view, add-to-cart, checkout, purchases, blended CAC, contribution margin, refunds and actual subscription cohort retention **on your own campaigns**.
- Existing competitors' ads are *examples and research inputs*; do not assign them guessed financial metrics.
- Do not attribute a positive outcome to an isolated creative change unless offer, targeting, landing-page and seasonality are controlled or at least recorded.

## 4. Repeat purchasing changes the economics

The interviewer notes the supplement business benefits from recurring customers; Adam describes losing subscription revenue amid payment-processing disruption. Product choice should therefore account for replenishment, replacement cycles, repairs, attachments, service contracts, and switching costs. A robot spare-parts subscription or recurring calibration service is only useful if an actual maintenance schedule and customer willingness-to-pay support it. Avoid forced subscriptions or confusing cancellation practices.

## 5. China's strategic role: terms, verification, capability

Adam says meeting his existing manufacturer revealed an in-house lab, helped negotiate terms and ultimately led to an unsolicited price reduction. These are not proof that any factory is reliable. An industrial-goods researcher should independently verify legal manufacturing identity, real production site, quality-system scope, reference customers, samples from production runs, component traceability and batch consistency.

**Supplier negotiation variables:** ex-works price; MOQ and MOQ per variant; deposit percentage; net terms; lead time; tooling ownership; inspection acceptance criterion; defects allowance; warranty reimbursement; spare-parts availability; packaging; compliance documentation; Incoterm; landed cost; exclusivity if justified. For electronics and batteries add genuine certification and import/transport requirements.

## 6. The negative case: delegation, automation and single points of failure

The first brand incurred sustained losses while the founder was removed from creative direction and avoided checking financial reports. Later, a payment-processing disruption damaged recurring cash flow. His AI experiment consumed a month without producing useful automations. The common cause is **unmeasured transfer of responsibility**. An agent, outsourced editor or processor is not an outcome guarantee. Create an owner, measurable SLA, rollback, anomaly alert and a budget for every delegated process. For a technical system, use job-level verification and freshness alerts rather than agent-generated "all green" summaries.

---

# PART II — PUBLIC COMPETITOR INTELLIGENCE: WHAT IS REAL

## 7. Storefront reconnaissance workflow

For any public storefront, collect its canonical domain; robots and terms; platform fingerprint; region/currency; public product links; accessible collection sorting; legal/business contact; public shipping and return policies. Do not assume every Shopify shop exposes `/collections/all`, `/products.json` or identical sorting behavior. On a multilingual storefront, capture locale and currency in every observation.

**Manual starting URLs:**
```
https://EXAMPLE.com/collections/all?sort_by=best-selling
https://EXAMPLE.com/products.json?limit=250&page=1
https://EXAMPLE.com/products/PRODUCT-HANDLE.js
https://www.facebook.com/ads/library/
```
The 250 number in Shopify's Ajax documentation refers to **variants per product JSON response**, and must not be mistaken for a guarantee that the unauthenticated collection-feed endpoint returns 250 products or is exposed on every shop. Test page sizes and response completeness. The storefront Ajax API is unauthenticated but subject to abuse prevention. [Shopify Ajax](https://shopify.dev/docs/api/ajax), [Shopify product JS](https://shopify.dev/docs/api/ajax/reference/product).

**Minimum provenance:** exact URL, fetch time in UTC, HTTP status, content type, content hash, parser version, locale, response bytes, terms review date, robots allowance, extraction confidence, *explicit null* for unavailable fields.

### Best-seller ranking caveats
- Based on **number of all-time orders that include a product**, not current orders, total units, profit, or revenue.
- Rank can shift with store removals, product launches, all-time counts and catalog mutations.
- Ranking across unrelated stores is not directly comparable without observing age, category and assortment size.
- A ranking rise is a *relative ordinal event*; infer neither transaction count nor absolute sales velocity.
- Distinguish automatic best-selling sort from manual merchandiser-selected presentation, or the store ignoring query parameters.

### Product JSON caveats
- Public prices are **retail asking prices**; promotions can be code-dependent or checkout-specific.
- `compare_at_price` indicates a comparison/list price, **not cost** or proven savings.
- Product `created_at` may reflect import/relisting, **not first sale** or original invention date.
- Availability may change by location or customer profile. Selling plans and bundles complicate headline price.
- Public products can be hidden from a particular channel, excluded from feed or duplicated.

## 8. Meta Ads Library workflow

Go to Meta Ads Library, search brand and spelling variants, verify matching advertiser page ID and website, select country and relevant ad category, preserve active status and observed first-delivery date. Record independent **seen_first_at** and **seen_last_at** timestamps. For competitor creatives, extract angle, first-three-second hook, presenter, claim, objection, product, offer, landing-page URL, creator relationship if disclosed, and placement. The public library is not an ad account analytics interface.

For EU/UK-delivered ads and political/issue ads, additional transparency and historical retention differ. Review the official API's field-level restrictions before promising automation: [Meta Library](https://www.facebook.com/ads/library/), [Meta API](https://www.facebook.com/ads/library/api/).

**Persistence signal:** ad observed running >= 60 days. Competing explanations: profitable acquisition; tiny retargeting audience; brand awareness; low-budget experimentation; operational neglect; long purchase consideration; evergreen seasonal content. Improve signal via *multiple independent ads*, creative diversification, new landing pages, positive product-review growth, and strong pricing discipline. **Never label a competitor ad profitable from public data alone.**

## 9. Additional external data families — by legitimate access path

| Source family | Examples | Observables | Access / cautions |
|---|---|---|---|
| Storefronts | Shopify collections, public Ajax product pages, JSON-LD Product | Product assortment, list price, variants, rank proxies | Availability and robots/ToS vary by site |
| Advertising | [Meta Ad Library](https://www.facebook.com/ads/library/), [Google Ads Transparency Center](https://adstransparency.google.com/), [TikTok Creative Center](https://ads.tiktok.com/business/creativecenter/) | Creative, messaging, disclosed geography and duration | Public UI vs permitted API differ; commercial spend mostly unavailable |
| Market demand | [Google Trends](https://trends.google.com/trends/), [Google Merchant Center](https://support.google.com/merchants/), [Google Search Console](https://search.google.com/search-console/about) **for owned sites** | Relative search interest and **owned** impressions | Trends is normalized, not absolute search demand |
| Marketplaces | [eBay Developer APIs](https://developer.ebay.com/), [eBay Product Research](https://www.ebay.com/sh/research), public Amazon listing pages | Public asks; approved sold-price / transaction research when eligible | Sold history and API entitlements must be validated per account/market |
| China supplier discovery | [Alibaba](https://www.alibaba.com/), [1688](https://www.1688.com/), [Made-in-China](https://www.made-in-china.com/), [Global Sources](https://www.globalsources.com/) | MOQ, quote, suppliers, lead times, documentation claims | Listed price often not firm; 1688 may need local buying assistance; no assumed public API |
| Components | [LCSC](https://www.lcsc.com/), [DigiKey API](https://developer.digikey.com/), [Mouser API](https://www.mouser.com/api-hub/), [Octopart/Nexar](https://nexar.com/) | SKU specs, authorized stock, lead times, price breaks | Approval, terms and quotas vary; never present a vendor listing as genuine without verification |
| Factories & compliance | [Companies House](https://developer.company-information.service.gov.uk/), [EU Safety Gate](https://ec.europa.eu/safety-gate-alerts/), supplier quality records, accredited labs | Entity checks, recalls, product constraints | Legal identity alone does not establish manufacturer capability |
| Review / support | Public authorized reviews, forum/product complaint trends, owned helpdesk | Failure modes, installation difficulty, common objections | Selection bias, fake reviews, PII restrictions |
| Shipping | [Freightos](https://www.freightos.com/), courier rate quotes, official customs schedules | Landed-cost sensitivity | Benchmark is not a committed freight quote |
| Data collection | [Common Crawl](https://commoncrawl.org/), [Internet Archive](https://archive.org/) | Prior public site snapshots | Archive coverage incomplete and rights/terms still apply |

**Research principle:** a source's existence is not proof that a free, open, complete, official API exists. Store a `rights_status` and `api_access_status` against every connector.

---

# PART III — 20 RESEARCH SIGNALS AND THEIR FALSIFIERS

**These are engineered hypotheses, not observed profit predictors. Each must be backtested out of sample.**

| ID | Signal / trigger | Minimum sources | Why inspect it | Main falsifier |
|---|---|---|---|---|
| S01 | New product reaches best-seller top quintile quickly | Timestamped storefront rank + launch | Early demand proxy | Small assortment / manual sort / relisting |
| S02 | Stable high rank while public price increases | Rank + price history | Apparent pricing resilience | Rank inertia from old sales |
| S03 | Many competing stores launch equivalent SKU in short window | Multi-store canonical matching | Emerging category | Shared catalog import / coordinated promotions |
| S04 | Competing sellers discontinue item but surviving seller maintains rank | Removal events + rank | Possible supply bottleneck | Legal recall, product defect, seasonality |
| S05 | Product rankings improve across independent geographies | Region-specific storefront observations | Broader cross-market interest | Same store feeds / currency artifacts |
| S06 | New creative angles appear simultaneously across unrelated brands | Verified advertiser IDs + creative classifier | New buyer awareness / market education | Agency template propagation |
| S07 | Long-running ad + more variants + new follow-on launches | Meta snapshots + catalog changes | Persistent investment signal | Brand campaign with low spend |
| S08 | Ad goes dark while product stays ranked | Ad history + rank | Channel or creative fatigue hypothesis | Tracking coverage or regional omission |
| S09 | Persistent ad points to frequently revised landing page | Ad destination + historical page snapshots | Active offer optimization | Automated template edits |
| S10 | Retail price unchanged while supplier cost drops | Store prices + verified quotes | Expanded potential unit contribution | Quote not executable at real MOQ |
| S11 | Identical component cheaper from verified authorized alternative | Manufacturer P/N + price break + stock | Repair BOM reduction | Counterfeit, incompatibility, customs |
| S12 | High resale sell-through + recurring repair complaint | Approved sold-price data + reviews | Repair service and spare demand | Unfixable fault / unsafe repair |
| S13 | Repeated warranty complaint but readily available spare | Public reviews + parts catalog | Aftermarket service opportunity | Manufacturer safety restrictions |
| S14 | Rapid model launch followed by scarce replacements | OEM launch + distributor inventory | Time-limited spare-parts opportunity | Closed parts ecosystem |
| S15 | Multiple ads advertise subscription with steep first-order discount | Ads + storefront selling plans | Potential LTV-driven acquisition | Cancellation, churn, refund sensitivity |
| S16 | Offer discount deepens while ad count stays high | Price + offer + ad observations | Competitive pressure / acquisition changes | Seasonal promotion / misleading compare price |
| S17 | Product removed around recall or compliance action | Site changes + official alerts | Compliance/fragility event | Unrelated redesign or catalog cleanup |
| S18 | Advertiser broadens from explanation to emotion | Ad angle history + new creative groups | Market sophistication hypothesis | Audience split / platform mix change |
| S19 | Brand moves from many generic SKUs into few unique SKUs | Catalog structure + trademarks / packaging | Differentiation investment | Temporary inventory shortage |
| S20 | Stable product price + supplier financing term improvement | Verified quotes + retailer economics **only if owned** | Working-capital opportunity | Quality deterioration / financing restrictions |

**Validation protocol for every signal:** record pre-specified event definition, source independence, control group and time window; test precision / recall of *observable* outcomes (e.g. next-quarter rank persistence or own pilot contribution), not imaginary competitor profits. Track false positives and revise the hypothesis with a new version, never rewrite historical labels.

---

# PART IV — UNIT ECONOMICS AND REAL COMMERCIAL FILTERS

## 10. Never equate visible retail price with gross profit

**First order contribution** = collected selling price − VAT/sales tax actually owed − product cost − inbound shipping/duties − outbound fulfilment − payment fees − expected returns/warranty provision − attribution-adjusted customer-acquisition cost.

**Repeat-order contribution** = incremental net receipts − incremental landed cost − fulfilment − transaction fees − servicing − refunds and churn provisions. Subtract replacement marketing spend where relevant.

**Working capital requirement** depends on supplier deposits, MOQ, inventory lead time, processor payout delay/reserves, advertising prepayment, refunds and safety-stock policy.

**Example (illustrative UK physical product, not Adam's figures):** public retail £80 inclusive of 20% VAT (net receipts £66.67 if standard-rated); landed product + inbound £28; fulfilment £6; fees £2; expected refunds/warranty £3; allowable acquisition cost for £10 target first-order contribution = £17.67. Increasing apparent compare-at price to £120 changes none of that. For a lower-priced spare, shipping and failure rates may dominate the economics.

## 11. Subscription cohorts and payment-concentration risk

A simple cohort model:
- cohort_size_t = new paying subscribers from acquisition month t
- active_{t,m} = cohort_size_t × survival probability to month m
- cash_in_{t,m} = active_{t,m} × net monthly price × successful billing probability
- cash_out_{t,m} = active_{t,m} × marginal goods/fulfilment/support cost + refunds + processor reserves
- cohort_contribution = sum(discounted monthly net cash flows) − initial CAC

Do not use a headline "LTV" without cohort retention, refunds, failed billing, pause/cancel behavior, and cash-flow timing. Counterparty failure matters even if reported dispute rates are low. Shopify Payments expressly allows reserves under its terms: [Shopify Payments Terms](https://www.shopify.com/legal/terms-shopify-payments). Backup providers must be permitted by contract and integrated lawfully; do not advise routing around account restrictions.

## 12. Pilot evaluation thresholds (proposals, not universal truths)

For a first low-capital repair parts or electronics intelligence pilot:
- require *at least two independent demand sources* (e.g. public catalog trend + actual sold-price history); ads alone are insufficient;
- quote *two credible suppliers*; separately record one sample order and one deliverable UK landed-cost quote;
- run bench compatibility tests on the actual model before publishing claims;
- compute conservative, base and optimistic contributions with explicit defect rates;
- validate *customer action* with a signed pilot, deposit, paid diagnostic or verified qualified lead rather than click volume alone;
- predefine exit gates (unsafe product, no reliable spare, unusable economics, zero paid conversions after capped test).

---

# PART V — THE POW SYSTEMS DATA GARDEN

## 13. The differentiated asset

**The product is not a generic Shopify scraper.** It is a continuously updated *evidence graph* that joins independent commerce observations to real hardware compatibility, component supply, secondhand value, repair outcomes and local trade capacity. The most promising initial application is **robotics and electronics repair**, because pure product scraping is easy to replicate but verified bill-of-materials matching and repair outcomes are not.

### L1 — Collect source truth

Keep **separate specialized source repos** (`powproducts`, `repair`, `powrobots`, `powphysical` and optionally `powuk`) and one central scheduler/catalog in `powops`. Each collector outputs immutable raw snapshots plus typed observations. `powk` defines shared contracts. Do not mix collector-specific parsing into the orchestration kernel.

**Starting refresh schedule (tune to terms and observed rates):**
- Daily: public product prices, new SKU discovery, supplier availability and selected best-seller ranks.
- Weekly: manual or licensed public ad-library observations, competitive creative annotations, supplier term reviews.
- Weekly/monthly: sold-price research, model-level repair trends, official safety/recall and regulatory changes.
- Event-triggered: owned campaign results, paid supplier quotes, verified failure reports and new OEM robot launches.

**Raw snapshot envelope**
```json
{
  "snapshot_id": "sha256-of-source-url-time-body",
  "source_id": "shop-public-brand-example",
  "collector": "powproducts.shopify-public@0.1.0",
  "observed_at_utc": "2026-09-22T00:00:00Z",
  "requested_url": "https://example.com/products.json?limit=50&page=1",
  "http_status": 200,
  "locale": "en-GB",
  "currency": "GBP",
  "rights_status": "reviewed-public-access",
  "robots_status": "allowed-at-observation-time",
  "content_sha256": "<sha256>",
  "blob_uri": "r2://pow-raw/shop/.../body.gz",
  "parser_version": "shopify-product-public-v1",
  "completeness": "partial-unverified"
}
```

`rights_status` here is an illustrative field, not a determination that any specific real website permits crawling. Never mark a source reviewed without actual review.

### L2 — Normalize entities and changes

Core entities: `store`, `brand`, `advertiser_page`, `product`, `variant`, `global_model`, `manufacturer_part`, `supplier_offer`, `robot_model`, `device_model`, `compatibility_claim`, `creative`, `ad_observation`, `listing`, `resale_transaction_observation`, `repair_job_outcome`, `source_evidence`.

Identity priorities:
1. Source-local immutable ID when available; immutable ad/library ID when available.
2. Exact manufacturer part number + revision + manufacturer (not generic keyword similarity).
3. EAN/GTIN/UPC where legitimate, recognizing reused/corrupt IDs.
4. Verified photo/spec/connector/voltage dimensional compatibility evidence.
5. Fuzzy match only as *candidate*, never an automatic verified match for critical components.

**Observation versus assertion:** `advertiser_page has active_ad` is an observation; `this brand has high ROAS` is an unsupported inference; `this board works in Unitree model X` needs bench/OEM evidence.

**Change types:** `FIRST_SEEN`, `PRICE_CHANGED`, `COMPARE_AT_CHANGED`, `VARIANT_ADDED`, `VARIANT_REMOVED`, `RANK_CHANGED`, `AD_FIRST_SEEN`, `AD_LAST_SEEN`, `CREATIVE_ANGLE_CHANGED`, `SUPPLIER_STOCK_CHANGED`, `SAFETY_ALERT`, `COMPATIBILITY_CONFIRMED`. Preserve old and new state and source links.

### L3 — Models (explicit uncertainty)

1. Rank-momentum proxy within one store, with censoring when collection changes.
2. Creative persistence conditional on observation coverage by country.
3. Cross-store listing diffusion and launch timing.
4. Supplier price distribution at MOQ, shipping destination and verified quality tier.
5. Resale-minus-repair contribution model from authorized sold transaction data.
6. Replacement-part supply lag by model/revision and geography.
7. Customer-objection clustering with supporting review excerpts under provider rights.
8. Forecast intervals for **your own** repair demand, using first-party pilots and service requests.
9. Counterparty and platform concentration stress tests for a hypothetical merchant.
10. Causal event studies: did source-independent interest change before the observed launch/promotion?

For uncertainty: include `evidence_grade` (direct invoice / supplier quote / public listing / estimated / unverifiable); confidence must be calibrated on held-out cases, not invented by the language model.

### L4 — Commercial endpoints

| Endpoint | Customer | Outcome sold | Why they might pay |
|---|---|---|---|
| `/v1/repair/opportunities` | UK independent repairer | Models/jobs matching skill, parts, resale demand and expected unit contribution | Saves sourcing/research time |
| `/v1/robots/parts/alternatives` | Robot service technician / integrator | Verified compatible spares with lead time, landed cost and evidence | Less repair downtime |
| `/v1/products/demand-changes` | Specialist reseller | Observed launches, assortment shifts, relative rankings and resale comps | Category scouting |
| `/v1/supplier/quotes` | Low-volume hardware founder | Side-by-side *actual quoted* suppliers, MOQ, lead times, QC flags | Avoids inaccurate marketplace price estimates |
| `/v1/creative/angles` | Brand strategist | Lawfully summarized competitor messaging evolution with links and dated observations | Better creative hypothesis generation |
| `/v1/merchant/risk-check` | Small merchant | Owned-data cash-flow/processor/vendor concentration scenario | Better operational decisions |

**First paid MVP:** a weekly **UK Robotics & Electronics Repair Opportunity Brief** with five tested opportunity cards, exact machine/revision, verified replacement part, source-backed recent sold-price comp, quoted landed cost, repair time assumption, safety/compliance check and confidence. Test willingness to pay *before* building a broad dashboard. The briefing can be agent-consumable JSON as well as PDF/email; frontend is secondary.

---

# PART VI — DATABASE DESIGN AND IMPLEMENTATION

## 14. Proposed PostgreSQL schema (minimum viable)

```sql
CREATE TABLE sources (
  source_id TEXT PRIMARY KEY,
  source_type TEXT NOT NULL,
  base_url TEXT,
  allowed_access TEXT NOT NULL DEFAULT 'pending_review',
  terms_checked_at TIMESTAMPTZ,
  cadence_seconds INTEGER,
  owner TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE raw_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  url TEXT NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  http_status INTEGER,
  content_hash TEXT,
  blob_uri TEXT,
  parser_version TEXT,
  completeness TEXT,
  collection_notes TEXT,
  UNIQUE(source_id, url, observed_at)
);
CREATE TABLE entities (
  entity_id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  canonical_name TEXT NOT NULL,
  canonical_key TEXT,
  verified BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE external_ids (
  source_id TEXT REFERENCES sources(source_id),
  source_entity_id TEXT NOT NULL,
  entity_id TEXT REFERENCES entities(entity_id),
  first_seen_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (source_id, source_entity_id)
);
CREATE TABLE observations (
  observation_id TEXT PRIMARY KEY,
  snapshot_id TEXT NOT NULL REFERENCES raw_snapshots(snapshot_id),
  entity_id TEXT REFERENCES entities(entity_id),
  field TEXT NOT NULL,
  value_json JSONB NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  locale TEXT,
  currency TEXT,
  evidence_grade TEXT NOT NULL DEFAULT 'public_observation'
);
CREATE INDEX observations_field_entity_date
  ON observations(entity_id, field, observed_at DESC);
CREATE TABLE relations (
  relation_id TEXT PRIMARY KEY,
  left_entity_id TEXT REFERENCES entities(entity_id),
  predicate TEXT NOT NULL,
  right_entity_id TEXT REFERENCES entities(entity_id),
  assertion_status TEXT NOT NULL DEFAULT 'candidate',
  evidence_snapshot_id TEXT REFERENCES raw_snapshots(snapshot_id),
  valid_from TIMESTAMPTZ,
  valid_until TIMESTAMPTZ
);
CREATE TABLE hypotheses (
  hypothesis_id TEXT PRIMARY KEY,
  version INTEGER NOT NULL,
  name TEXT NOT NULL,
  pre_registered_rule JSONB NOT NULL,
  falsifier TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE signal_events (
  signal_id TEXT PRIMARY KEY,
  hypothesis_id TEXT REFERENCES hypotheses(hypothesis_id),
  entity_id TEXT REFERENCES entities(entity_id),
  triggered_at TIMESTAMPTZ NOT NULL,
  observation_ids TEXT[] NOT NULL,
  coverage_score REAL,
  result_status TEXT NOT NULL DEFAULT 'unvalidated'
);
CREATE TABLE repair_verification (
  case_id TEXT PRIMARY KEY,
  device_entity_id TEXT REFERENCES entities(entity_id),
  part_entity_id TEXT REFERENCES entities(entity_id),
  test_method TEXT NOT NULL,
  tested_by TEXT,
  test_date DATE,
  compatibility_status TEXT NOT NULL,
  failure_notes TEXT,
  evidence_snapshot_id TEXT REFERENCES raw_snapshots(snapshot_id)
);
```

**Operational requirements:** logical immutable snapshot storage (e.g. R2), relational extracted facts (PostgreSQL), cheap Parquet export for backtesting, job scheduling, secret isolation, source-specific rate limits, dead-letter queue, versioned parser and *independently rendered* dashboard showing actual proof of fetch and extraction. Hashes provide tamper evidence, not proof that the source itself was true.

## 15. Build plan in five milestones

**M0 — Reality checks (day 1):** Choose ten explicitly allowed public storefronts in robotics/electronics, test which discovery endpoints actually work, document robots and terms, and establish at least one legitimately accessible Meta workflow. Record non-working sources instead of silently dropping them.

**M1 — L1 growing (week 1):** Four collectors: compliant public storefront, authorized component distributor, supplier quote inbox/manual capture, official safety/recall. Raw R2 blobs and job dashboards; historical backfill only through licensed/publicly permitted archives. Seed with 25 real machines/SKUs across two repair categories.

**M2 — Normalization (week 2):** Canonical model and part IDs, currency/region/pack-size normalization, timestamped price changes, explicit SKU-match confidence. Add mechanical compatibility tests on a small pilot subset.

**M3 — Intelligence (weeks 3–4):** Launch S01, S10, S11, S12, S14 and S17 first: they can be checked against public evidence or small first-party pilots. Score *data quality* rather than theoretical upside; run negative-control categories.

**M4 — First commercial validation:** Publish 5 opportunity cards; ask 10 real repairers or integrators whether they'd act; recruit 1–3 paid trials; measure actual job sourcing, repair completed, realized contribution and refund rates. If nobody pays, adjust the customer problem rather than adding more dashboards.

### Source reliability tests
- **Completeness:** compare collected product count with visible paginated collection count; alert when coverage falls materially.
- **Freshness:** last successful fetch and *last meaningful new snapshot* separately; stale HTTP 200 is not fresh data.
- **Price validity:** currency, tax basis, shipping destination, MOQ, stock and quote expiry.
- **Identity:** duplicate-rate; manually inspect a random sample of merges and all safety-critical compatibility assertions.
- **Change detection:** fixture of deliberately changed pages; prove collector catches price/variant/rank/removal without false positives.
- **Signal validation:** store precision/recall with known labels and explicitly mark unobservable profitability.
- **Compliance:** source owner, permit date, ToS change reminder, deletion/takedown process and rights limitations on copyrighted creatives.

### Agent-ready execution brief

> Implement a source-respecting L1 garden in `powproducts` for public Shopify catalog observations and, if permitted, selected collection rank observations; a manual/approved Meta creative-observation workflow; source provenance, HTTP status, parser version, raw R2 snapshots, change events and a minimal monitoring API. Define contracts in `powk`, coordinate in `powops`, join products to verified physical parts through `powphysical`, repair outcomes through `repair`, and robot model/revision through `powrobots`. Do **not** infer competitor sales, ROAS, margins, component compatibility or active ad spend from public proxies. Every collector must have rate limits, access-rights metadata, resumable pagination where actually supported, fixture tests, raw-body hashes, field-level confidence, freshness metrics, dead-letter queue and a kill switch. Success criterion: seven consecutive daily runs with no silently missing sources, full raw snapshot replay and 20 manually checked changed observations. Defer L3 and dashboards until L1 evidence quality is demonstrated.

---

# PART VII — RESEARCH OPPORTUNITIES AND HARD QUESTIONS

## 16. Twenty further lines of investigation

1. **Price elasticity without transaction access:** can the direction of relative best-seller-rank change after a natural price shift provide *any* useful proxy after controlling assortment changes? Do not equate rank movement with units.
2. **Creative life-cycle curves:** estimate the distribution of public ad durations for product category and page; measure each brand's baseline before labeling an ad unusually persistent.
3. **Creative refresh versus product persistence:** link ad starts/stops to catalog rank changes; use brand and season fixed effects and compare similar products.
4. **Global launch-lag maps:** trace similar physical SKUs from Chinese manufacturers to UK/US retail first-seen dates; beware relabeling and shared images.
5. **Cross-store offer dispersion:** same verified product across stores, normalized for shipping, VAT and warranty.
6. **Variant proliferation:** whether rising colour/capacity/size variants precede subsequent SKU survival; control for catalog import.
7. **Refund-risk proxies:** triangulate public review themes, safety recalls and own pilot failures; never infer exact competitor return rates.
8. **Claim-risk classifier:** flag health/efficacy statements against FTC/CAP official rules for human review (not automated legal verdict).
9. **Manufacturer realness:** evidence scoring from legal entity, physical site, third-party audit scope, sample traceability and actual purchase outcomes.
10. **Supplier negotiation outcomes:** build first-party quoted cost histories for repeatable MOQ/lead-time comparison.
11. **Repairable-by-design opportunities:** BOM and teardown complexity, tool requirements, spare availability and published safety restrictions.
12. **Robot aftermarket map:** serviceable components by OEM, model, revision, warranty terms and skill requirements.
13. **UK technician opportunity map:** verified course credentials and actual local customer requests, not inferred employment claims.
14. **Resale liquidity:** sold comp count and time-to-sell from legitimately accessible datasets, adjusted by condition and location.
15. **Stockout versus discontinuation:** multi-snapshot product and distributor availability; avoid single-fetch conclusions.
16. **Component authenticity:** authorized supply and lot traceability as a differentiated paid evidence layer.
17. **Subscription shock resilience:** first-party merchant scenario testing under failed billing, reserve increase and churn stress.
18. **Creative hypothesis ledger:** tie every newly proposed angle to the exact market observation that inspired it and the test outcome on your own ads.
19. **Maintenance subscriptions:** actual repeat jobs and predictive replacement intervals where OEM specs and field evidence exist.
20. **Agent-first delivery:** expose verifiable JSON with `why_this_card`, evidence refs, costs, uncertainty, last verified and `do_not_claim` fields to user-controlled assistants.

## 17. Stop conditions

Do not expand a dataset or launch a business solely because the information is easy to scrape. Stop when the source is contractually restricted; an ad proxy cannot be linked to an outcome; supplier quotes aren't actionable; support burdens overwhelm contribution; a robotic part cannot be bench-verified; there is material safety or regulatory ambiguity; market participants won't pay for a high-quality opportunity card; or time spent on orchestration exceeds time spent validating real commercial demand.

---

# PART VIII — DIRECT SOURCE DIRECTORY

**Primary source:** User-supplied 40-minute interview transcript, titled by source chapters *Adam's Ecom Journey at 19* through *Dealing With Losses and Imposter Syndrome*, timecodes 0:53–40:04. Self-reported statements are cited by time above.

**Official public-source validation:**
- Shopify Help — collection sorting, all-time best sellers: https://help.shopify.com/en/manual/products/collections/collection-layout
- Shopify Ajax — unauthenticated API, limitations: https://shopify.dev/docs/api/ajax
- Shopify product JS reference: https://shopify.dev/docs/api/ajax/reference/product
- Shopify Storefront API — authenticated integration alternative for **your own or authorised merchants**: https://shopify.dev/docs/api/storefront/2026-01
- Meta Ads Library — advertiser searches and coverage: https://www.facebook.com/ads/library/
- Meta Ad Library API — availability / field restrictions: https://www.facebook.com/ads/library/api/
- Google Ads Transparency Center: https://adstransparency.google.com/
- TikTok Creative Center: https://ads.tiktok.com/business/creativecenter/
- FTC Health Products Compliance Guidance: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- ASA / CAP food and supplement ad rules: https://www.asa.org.uk/type/non_broadcast/code_section/15.html
- Shopify Payments merchant legal terms: https://www.shopify.com/legal/terms-shopify-payments
- eBay Developer APIs: https://developer.ebay.com/
- eBay Product Research: https://www.ebay.com/sh/research
- DigiKey API: https://developer.digikey.com/
- Mouser API: https://www.mouser.com/api-hub/
- Octopart/Nexar: https://nexar.com/
- Companies House Developer API: https://developer.company-information.service.gov.uk/
- EU Safety Gate: https://ec.europa.eu/safety-gate-alerts/
- Common Crawl: https://commoncrawl.org/
- Internet Archive: https://archive.org/

**Final framing:** Successful public-competitor intelligence is not "they ran an ad for 60 days, so copy it." It's "we can observe a dated sequence of product, message and supply decisions, detect a change, connect it to multiple independent pieces of evidence and test an opportunity cheaply in the real world." That is the data garden worth growing.
