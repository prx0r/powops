# Sharpening POW: from robot parts to robotics procurement infrastructure

The critique identifies a genuine problem with the current POW vision: we have been treating several different customer markets as though they were one. But I disagree with its conclusion that selling robot parts and providing infrastructure for people building robots must be completely separate businesses.

They can share an extremely valuable underlying system. What should remain separate are their customers, commercial products and acquisition strategies.

I'd sharpen POW's thesis to:

Build the UK robotics parts and procurement graph: every supported robot, the parts it uses, compatible alternatives, the suppliers that sell them, and the actual economics of obtaining them. Make that intelligence available to repair businesses, robotics builders and AI agents.

The distinctive opportunity isn't competing with Amazon on replacement brushes. It's becoming the service that knows what physical parts a robot needs and how to obtain them.

## 1. The first correction: focus on robot models, not component catalogues

The most revealing evidence from the research is the difference between existing catalogues and the information needed to act on them.

iRobot already operates a UK parts store covering numerous Roomba generations, with official filters, brushes, batteries and replacement modules. Its service-parts catalogue also includes replacement wheel modules and cleaning heads. Therefore, an independent replacement-parts store would be entering an established market, not an uncontested niche.

At the other end, Hugging Face's SO-101 robotic arm has an openly documented bill of materials. Its leader arm uses different servo gear ratios at different joints, while the follower arm has its own configuration. This means sourcing the right model and revision matters much more than simply finding the cheapest servo motor.

These two markets have the same fundamental data problem:

THE SHARED POW DATA MODEL

Robot model and exact revision

Verified bill of materials and replacement parts

Compatible substitutes and required specifications

Chinese and UK suppliers, stock and historical prices

Verified UK delivered cost, lead time and purchase options

A robot vacuum owner asks which wheel module fits their machine. A developer asks which servos, controllers and fabricated components will complete an SO-101 build. POW resolves both through the same type of data infrastructure.

This does not mean they use the same components, or should visit the same storefront. It means we can reuse the difficult work: matching physical products across inconsistent catalogues, checking compatibility, calculating delivery economics and learning from actual purchases.


## 2. Which robotics markets to enter

| Market | Role in POW |
| --- | --- |
| Robot vacuums | Existing replacement demand; an initial repair-parts and procurement experiment |
| Open-source robotic arms and rovers | Build-to-order BOMs and the foundation for the future AI robotics platform |
| Robotic lawnmowers | A business-to-business opportunity involving installation, servicing and replacement parts |
| Generic electronic components | Supporting supplier data, not a standalone retail category |
| Toys and novelty AI gadgets | Outside the initial scope |

I would start with two small, measurable datasets: replacement parts for a tightly selected group of robot vacuums, and complete BOMs for a few open-source robotics projects. Launch only one paid workflow initially, determined by actual customer demand.

The distinction is important. A robot vacuum parts business can potentially generate revenue from existing failures and scheduled consumable replacements. But it won't automatically establish POW as infrastructure for robotics developers. That second business needs exact technical specifications, BOM versioning, firmware compatibility and fabrication information.

The proposed builder market is also competitive. The Pi Hut already sells robotics kits, motor controllers, servos, chassis and development hardware in the UK. POW would need to outperform generic component search by delivering complete, verified project-specific baskets and reliable alternatives.

The critique's claims that robot vacuum parts have limited competition or attractive margins still need validating. Neither search interest nor the existence of cheap Chinese listings establishes profitable UK demand.

## 3. Build a BOM-to-purchase engine, not a robot-control SDK

This is where your idea of becoming the backend for AI-built robots becomes concrete.

A builder provides a GitHub repository, BOM or supported robot design. POW identifies the required components and versions, checks availability and offers complete purchasing options: fastest delivery, lowest landed cost, or a mixed basket with an acceptable delivery deadline.

The manufacturing side can be added incrementally. JLCPCB now documents APIs covering PCB fabrication, electronic components and 3D printing, including quotes and order management. Its September 9, 2026 guidance confirms that access requires an application and is not guaranteed. Seeed Fusion already accepts structured BOMs and offers human procurement assistance when parts cannot be matched automatically.

That makes a practical early version of your Printify analogy possible without owning manufacturing equipment. But complete mechanical assembly, calibration, final testing and product responsibility are separate services. They should not be presented as solved merely because the parts and fabrication can be ordered.

An API that reliably converts a supported robot design into an available, correctly specified, UK-deliverable parts basket is already a meaningful product. It doesn't need to write firmware, train robot policies or compete with LeRobot.

## 4. Correct the electrician thesis

Robotics remains a possible route into the trades, but the first customers should be people who already work on the relevant machines.

Husqvarna provides a useful example. Its UK robotic mower range includes model-specific spare parts and an established network of authorized servicing dealers. Those dealers provide diagnostics, replacement, installation and maintenance. Husqvarna also explicitly excludes electrical installation from its standard robotic mower installation service.

Consequently, targeting electricians immediately is a weaker proposition than targeting actual robot repair workshops, lawnmower servicing businesses and electronics technicians.

Keep electricians in POW UK's future customer strategy, particularly where their existing work overlaps with controls, charging, power supply and automation. First prove that robotics parts procurement solves an expensive problem for people already buying these parts.


## 5. Make POW's data moat much harder to copy

The critique concentrates on sourcing cheaper parts from China. That is useful, but supplier price aggregation alone is a fragile moat. Once another agent has access to the same supplier catalogue, it can perform much of the same comparison.

POW needs to accumulate information that cannot easily be reconstructed later: verified part compatibility, model revisions, actual UK delivery times, supplier failures, replacement outcomes and historical costs.

LCSC's documented API supports component discovery, pricing and order workflows. Alibaba has its own developer platform, but applications and API permissions require approval. Rather than attempt to scrape every Chinese supplier immediately, begin with dependable, permitted sources and expand where the data adds measurable value.

Each observation should preserve the original supplier evidence, the time it was observed, the applicable quantity and the confidence in its compatibility. A manufacturer-approved part, a seller-claimed equivalent and a replacement successfully tested by a repairer are three different things.

POW's proprietary measurement should be the cheapest reliable way to complete a particular physical job, not simply the cheapest listed part.

There are two further corrections to the critique's economics. The UK does not apply one universal import-duty percentage to electronics; the treatment depends on the item and circumstances, with special VAT rules for consignments of £135 or less. VAT-registered businesses may also be able to recover qualifying input VAT.

Model all of this at transaction level.

Similarly, don't commit to a UK warehouse or third-party logistics provider before identifying actual fast-selling products. Start with available UK distributors and approved overseas suppliers, record genuine order outcomes, then hold inventory only where the expected speed and margin justify it. Treat lithium batteries separately: their transportation requires appropriate testing and documentation, and importing or selling them can introduce additional UK producer obligations.

## 6. Muse strengthens the infrastructure argument

This is an important change since our previous POW discussions.

Meta launched Muse in the US on September 8, 2026, with the ability to carry out user-authorized tasks and purchases. Meta says Shop Pay is planned, while Shopify now supports distributing eligible product catalogues through agentic storefronts. However, Shopify's current Meta direct-checkout eligibility is limited to sellers serving the US, Canada and Mexico. It is not yet a ready-made UK acquisition channel for POW.

There is also an access risk. On September 22, reporting indicated that Amazon had blocked Muse from making purchases on its marketplace because of disputed access practices. This reinforces the value of direct, authorized supplier integrations instead of relying on an agent to browse and purchase from any website.

Build the purchasing API first, with an MCP interface and explicit customer approval for purchases. Connect it to Muse and other agents wherever supported. POW should own the specialist procurement intelligence, not depend on owning the interface through which customers interact with it.

## 7. What this changes in the existing repositories

This sharpens the division of responsibilities across the current POW project without requiring another collection of competing repositories.

| Repository | Responsibility |
| --- | --- |
| `powrobots` | Robot models, revisions, assemblies, BOMs and verified compatibility |
| `powproducts` | Canonical components, manufacturer part numbers, specifications and product identity |
| `powphysical` | Supplier offers, prices, availability, shipping and fabrication services |
| `repair` | Faults, replacement requirements, repair economics and actual repair outcomes |
| `powuk` | UK repair businesses, qualifications, service opportunities and local demand signals |
| `powk` / `powops` | Common data contracts, historical transformations, collection monitoring and service interfaces |

The critical architectural rule is to maintain one canonical part identity and one versioned compatibility graph. Individual collectors must not independently decide that differently named Chinese listings are interchangeable.

Keep the L1 collectors independent, but make their output usable together through a small shared set of identifiers and contracts. Above that, the first commercially useful transformation is model or BOM to verified purchasable basket.

## 8. The next concrete checkpoint

## POW Robotics: initial commercial proof

Build and verify one complete sourcing workflow using a small, curated catalogue rather than attempting to cover the entire robotics market.

0 of 5 milestones completed

Select 10 identifiable robot vacuum models and 2-3 open-source robotic designs, including the SO-101.

Resolve their exact parts and revisions, separating verified compatibility from untested alternatives.

Capture supplier offers and produce UK-delivered quotes for a useful subset of replacement and build parts.

Complete several manually supervised purchases or customer referrals, recording delivered cost, time and part correctness.

Use those outcomes to determine whether the first paid service is repair-shop procurement or project-based BOM sourcing.

The measure of success isn't the number of products in the database. It is how frequently POW can produce a correct, competitive, executable quote and whether customers return to use it.

My proposed refinement of the overarching thesis is therefore: POW is the procurement and compatibility intelligence layer for physical robotics. Repair parts provide existing demand, open-source robots provide the pathway into AI-assisted hardware creation, and transaction outcomes create the proprietary data that strengthens both businesses.


---

# POW Work: connecting tradespeople to robotics opportunities

Yes. I think this changes POW's commercial vision quite substantially. Rather than using robot repair to recruit electricians, POW could help existing tradespeople expand into home robotics, automation and other emerging technical work.

The incentive becomes much more compelling: connect your existing business to POW, discover additional work you could undertake, find the equipment you need, and get assistance quoting and bidding for those jobs.

There is an established adjacent market. CEDIA already offers UK training and professional certifications for home technology installers. Its February 2026 Smart Home Assurance Programme also connects qualified installers with homebuilders.

POW could extend that model towards robotics, with sourcing intelligence and opportunity discovery as its differentiators.

I would distinguish between two markets: home laboratories, where hobbyists and developers build robots and electronic projects, and home robotics and automation, where tradespeople install, maintain and repair equipment for paying customers. Both use parts of the same POW database, but the second is the more natural route to recruiting tradespeople.


## The bigger opportunity: POW Work

Imagine a gardener, an electrician, an electronics repairer and a home automation installer each connecting their business to POW. Rather than offering everyone the same robotics products, POW identifies new services each could offer using their existing skills.

| Existing business | Potential new market |
| --- | --- |
| Gardener or landscaper | Robotic mower installation, servicing and fleet maintenance |
| Electrician | Charging infrastructure, automated lighting, sensors and suitable robotic installations |
| IT or networking technician | Home automation, robotics networking and local AI systems |
| Electronics repairer | Robot diagnostics, component replacement and refurbishment |
| General tradesperson or maker | Enclosures, mounting, fabrication and assembly for custom robotics projects |

An important distinction: these are potential adjacent services, not a claim that every trade is qualified to perform them. POW would need to understand qualifications, insurance, manufacturer authorizations and the actual technical requirements of each job.

## Connect opportunities directly to POW's parts database

This is where the earlier Data Gardens work becomes especially useful.

## Example: a landscaping company connects to POW

Illustrative workflow, not a live job

1. Discover new work

   POW identifies a robotic lawnmower installation or maintenance opportunity in the company's service area.

2. Determine eligibility

   It checks the company's equipment, skills, qualifications and any required manufacturer training. It flags missing capabilities.

3. Price the job

   POW uses its robotics graph to identify the equipment and parts, compare UK and Chinese suppliers, and calculate a quote incorporating labour, shipping and risk.

4. Prepare the bid

   The company receives a suggested quotation, evidence and application checklist, with the owner approving submission.

5. Procure and complete

   Once the customer accepts, POW helps purchase the parts and records actual costs, delivery, installation and servicing outcomes.

Now imagine a homeowner designing a custom robot with an AI assistant. POW could provide a verified BOM and source the parts, then identify local businesses capable of 3D printing the enclosure, wiring the electronics or assembling the machine.

That creates a two-sided network: businesses use POW to find work, and robot builders or customers use POW to find people who can make their designs real.

## The public-tender opportunity already has usable data

The UK publishes procurement information that POW can collect, normalize and match to businesses. Contracts Finder has a documented notice-search API, while Find a Tender publishes structured public procurement data.

There is evidence of robotics-related procurement. For example, United Utilities published a February 2026 market-engagement notice seeking robotic inspection capabilities for difficult-to-access infrastructure, explicitly identifying SME suitability. That opportunity's engagement deadline has passed, but it demonstrates the type of specialized demand POW could track.

The distinction is that tender alerts alone are already available from public services. POW's commercial opportunity is helping a business determine whether it can fulfil a contract, what it needs to buy, whether subcontracting is required, and what the work would cost.

## How I'd integrate this without diluting POW

Keep robotics procurement as the specialist foundation and add an opportunity layer through `powuk`. That layer should connect four things: the job's requirements, a company's verified capabilities, the equipment and suppliers needed, and the economics of delivering the work.

Your existing repositories already map naturally to these responsibilities. `powrobots` and `powproducts` identify machines and components; `powphysical` prices and sources them; `repair` records interventions and outcomes; and `powuk` discovers opportunities, training routes and relevant local businesses. `powops` monitors the collectors and the resulting workflows.

I wouldn't build a general trades marketplace yet. That would put POW in competition with established lead-generation platforms before its specialist data offers a sufficiently differentiated service.

## The sharpened POW thesis

Build the intelligence infrastructure that connects physical robotics, global components, qualified local businesses and real commercial opportunities.

Parts data -> feasible jobs -> procurement -> verified outcomes -> better parts and opportunity intelligence.

The first commercial experiment I'd run is robotic lawnmower procurement and servicing opportunities for existing landscaping and repair businesses. It keeps the scope firmly inside robotics, creates a clear reason for tradespeople to connect, and allows the parts database and opportunity engine to develop together.

The longer-term proposition is broader: connect your business to POW and discover which emerging technical markets you can enter, what equipment you need, and how to deliver the work profitably. That could eventually become a genuinely useful capability for a trade business's AI assistant, without POW having to own the assistant itself.
