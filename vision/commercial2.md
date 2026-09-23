# POW Robotics: the data gardens and the money

The commercial model I'd build is a robotics parts and manufacturing network that earns money from transactions, with a growing proprietary database underneath it.

The gardens are not the product customers buy. They continuously discover new robots, identify their parts, compare global suppliers and learn from actual orders. POW then sells the ability to source, repair or manufacture physical robots.

The web research reveals an important distinction: existing manufacturers already offer substantial parts of the Printify vision. JLCPCB has APIs for component sourcing, PCB fabrication and 3D-printing quotes, while Seeed Fusion accepts BOMs and handles component procurement and PCB assembly.

POW shouldn't reproduce their factories or become another generic electronics distributor. Its opportunity is coordinating the work they don't collectively solve: identifying the right parts for a particular robot, combining multiple fabrication and sourcing services, and delivering a complete, usable machine.

## 1. Set up three interconnected gardens

Garden 1

## UK robot intelligence

Discover new consumer robots entering the UK, their exact models and revisions, parts, manuals, accessories and service requirements.

Output: a continually expanding robot-to-parts compatibility graph.

Garden 2

## Global parts and manufacturing

Track components, Chinese suppliers, UK stock, actual delivered prices, lead times, fabrication services and assembly partners.

Output: the cost and feasibility of buying or manufacturing something.

Garden 3

## UK work and capabilities

Track repair businesses, technical training, robotics installation opportunities and relevant procurement notices. Record what individual businesses are qualified and equipped to undertake.

Output: match real jobs to the businesses and equipment required to complete them.

Every garden shares identifiers and historical records. One robot component might appear in all three: as a replacement part, as a sourcing opportunity and as a requirement for a repair contract.

The first paid product uses Gardens 1 and 2. Garden 3 initially grows alongside them rather than turning into an entirely separate trades marketplace.


## 2. How the gardens make money

I found four potential revenue streams. They have different economics and should be introduced at different stages.

| Product | Customer | Proposed pricing |
| --- | --- | --- |
| Replacement parts and curated robotics kits | Consumers and robotics builders | Retail margin on each order |
| BOM sourcing and custom manufacturing | Robotics builders and AI applications | 10–20% service markup, subject to actual costs |
| Procurement intelligence and API | Repair businesses, retailers and app developers | £49–£299/month initially |
| Robotics work and procurement service | UK repairers and specialist trades | Subscription or fee on completed procurement |

These are proposed prices to test, not established market rates.

The initial paid experiment

# One-click UK robotics kits

A customer selects a supported open-source robot design. POW supplies the exact parts, an optimized purchasing basket and optional 3D-printed components, with one quote and one checkout.

Illustrative order economics

| Item | Amount |
| --- | --- |
| Customer pays | £180 |
| Parts, fabrication and shipping | £130 |
| Payment, fulfilment and returns allowance | £15 |
| Contribution before fixed costs | £35 |

Hypothetical figures, not an actual SO-101 quotation. Excludes marketing, salaries, product development and tax obligations.

This resembles Printify's commercial mechanics: merchants pay a fulfilment price, while the platform earns a margin on production orders. Printify explicitly states that its free platform makes money from fulfilment rather than requiring every merchant to subscribe.

But don't start with an assembled custom robot. Start with documented component bundles, outsourced printed components and manually approved procurement. Complete assembly requires more quality assurance and accountability.

## 3. Why a general BOM API won't be enough

There's already a free, open-source project called 1clickBOM that helps users fill shopping carts across distributors, including LCSC, Mouser and RS. Nexar also offers electronic component supply-chain data, with an evaluation API plan allowing up to 100 matched parts.

So a generic parts comparison API has existing alternatives. POW has to do something materially different.

The commercially useful output should be a complete, executable robotics build or repair quote. It needs to understand mechanical parts, exact servo versions, compatible electronics, multiple manufacturing processes and UK delivery—not just semiconductor SKUs.

For repairers, it should distinguish official spares, tested alternatives and unknown compatibility. For AI-generated designs, it should flag missing parts and unsupported assumptions before money is spent. The transaction itself then produces feedback the catalogue could not provide.


## 4. What needs changing in your existing repositories

I also checked the current GitHub repositories. You already have much of the foundation, so creating three more repositories would mostly increase management work.

| Repository | Next responsibility |
| --- | --- |
| [powrobots](https://github.com/prx0r/powrobots) | UK robot launch detection, robot model registry and BOM discovery |
| [powproducts](https://github.com/prx0r/powproducts) | Canonical part identity, exact revisions and verified compatibility |
| [powphysical](https://github.com/prx0r/powphysical) | Supplier offers, landed-cost quotations and manufacturing orders |
| [repair](https://github.com/prx0r/repair) | Faults, repair procedures, replacement outcomes and repair economics |
| [powuk](https://github.com/prx0r/powuk) | UK opportunities, technical training and service-provider discovery |
| [powops](https://github.com/prx0r/powops) | Monitor all the collectors and expose their coverage and failures |

There are two architectural issues to resolve immediately.

First, `powrobots` and `powproducts` both describe product identities and compatibility. Make `powproducts` the authoritative identity registry; `powrobots` should contribute robotics-specific evidence rather than maintain a conflicting catalogue.

Second, `powops` still documents its main monitoring inventory around the earlier crypto, repair, UK and stock gardens. Add the robotics, products and physical-supplier collectors to the same monitoring system. Check the actual deployed configuration first; I verified the repository documentation, not your VPS.

The `powphysical` repository also contains a peer-review document identifying potentially serious resolver problems, including incorrect voltage compatibility checks, missing-part omissions and placeholder prices. Verify whether those issues remain before accepting any automatically generated purchasing quote.

## 5. The actual collection plan

Proposed initial sources and collection cadence

| Dataset | Initial source | Cadence |
| --- | --- | --- |
| UK robot models | Official manufacturer catalogues and launch announcements | Daily |
| Model BOMs | Manufacturer documentation, LeRobot repositories and open hardware projects | On release or revision |
| Replacement parts | Official manufacturer stores and authorized parts distributors | Daily |
| Electronic components | LCSC, then approved UK distributor APIs | Every 6–24 hours |
| Fabrication | JLCPCB, PCBWay and Seeed, subject to access | Quote on demand |
| Repair history | Your own orders, customer feedback and licensed repair datasets | Per event |
| UK opportunities | Existing POW UK tender and training collectors | Existing cadence |

LCSC's documented API supports product searches and detailed component records, including pricing in supported currencies. JLCPCB provides fabrication and component APIs, but applications are individually reviewed. PCBWay also offers a partner API covering PCB quotations and ordering.

For repair parts, the iRobot UK catalogue is a useful initial reference: it lists genuine Roomba replacement components, including wheel modules and cleaning heads. The opportunities to investigate are discontinued models, unavailable parts and credible alternative suppliers—not merely undercutting official retail prices.

Every collection should preserve its timestamp, original evidence, source permissions and exact part identifiers. Don't automatically publish or commercially redistribute data simply because a website makes it publicly accessible. For example, iFixit's repair API distinguishes free non-commercial use from commercial access requiring an arrangement.

## 6. The first 30-day commercial experiment

I would concentrate on one transaction that uses the infrastructure you want to build anyway.

1. Week 1 — Build the catalogue

   Select a handful of established robot vacuum models and one open-source robotic arm, beginning with the SO-101. Resolve the exact parts and record reliable sources.

2. Week 2 — Generate real UK quotations

   Source a complete supported robotics kit and several replacement assemblies, recording actual delivered prices and suppliers. Reject baskets containing unresolved or unverified substitutions.

3. Week 3 — Test paid demand

   Offer manually supervised UK kit procurement and parts sourcing. Use a simple order form and payment flow rather than a sophisticated frontend. Record enquiries, completed orders and actual contribution margins.

4. Week 4 — Expose the first API

   Provide model lookup, verified parts, basket quotations and order status. Let an AI agent request quotes, but retain explicit human approval for manufacturing and purchases.

A practical initial commercial milestone would be ten genuinely paid orders, rather than a large but untested parts catalogue. The orders establish whether customers value POW's coordination enough to cover its costs.

## 7. The compounding business

## How transaction revenue becomes a data moat

A customer orders a robot kit.

POW records which parts were actually available, which suppliers delivered on time, which substitutions worked and what the real landed costs were.

The next quotation becomes more reliable.

Better purchasing information can support a procurement API, attract more builders and repair businesses, and generate more verified transactions.

Manufacturing becomes the next service.

Once POW can repeatedly source supported designs and coordinate reliable fabrication, expand from component baskets to assembled, tested robots using qualified manufacturing partners.

This gives your original Data Gardens thesis a direct commercial feedback loop. Continuous collection builds the history, but actual transactions validate the information and reveal which measurements customers will pay for.

The UK training and work-opportunity garden can follow once there is genuine procurement demand from repairers or builders. There is already an established robotic mower servicing and training ecosystem through manufacturers such as Husqvarna, so POW would need to offer demonstrably useful sourcing or new-work intelligence rather than another generic directory.

The near-term business is paid robot-parts and kit procurement. The longer-term business is an API through which any AI application can source and eventually commission the manufacture of a physical robot. The gardens are the infrastructure that allows both to improve with every new model, supplier observation and completed order.

This is a proposed deployment and commercial plan; I have not modified your repositories or started new collectors.
