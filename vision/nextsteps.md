I'd make robot maintenance, repair and parts intelligence the central focus of POW, with power tools and workshop equipment as a closely related second market.

The opportunity is bigger than selling robot components. Imagine a UK electrician, independent repairer or robotics technician asking POW:

"I've got a Unitree robot with a failed knee actuator. What part do I need, what does it cost from China versus the UK, how do I diagnose and replace it, what tools are required, and is the repair economically worthwhile?"

POW should eventually be able to answer that entire question with verifiable evidence.

The data architecture needs to connect six things: robot models, individual components, failure and repair knowledge, global parts suppliers, specialist tools, and the businesses qualified to perform the work. Your existing `powrobots`, `repair`, `powproducts`, `powphysical` and `powuk` repositories can cover these without introducing another isolated project.


# 1. Robot manufacturers: the core data sources

The first major finding is that manufacturer documentation varies enormously. Some companies publish detailed mechanical models and repair procedures; others keep spare-parts information inside dealer portals.

For Layer 1, these are the sources I'd begin with:

| Source | Data worth collecting | Access |
| --- | --- | --- |
| Unitree's official robot models | Robot geometry, joints, model variants, motor configurations | Open-source repository |
| Unitree documentation | Motor specifications, control interfaces and robot-specific documentation | Public web |
| Universal Robots manuals | Joint replacement, fault codes, calibration and servicing procedures | Public web |
| Universal Robots parts catalogue | Official replacement parts and accessories | Account required for download |
| FANUC MyPortal | Spare parts, alarm codes, manuals and service histories | Customer access |
| ABB Robotics | Parts, repair kits, exchange units and servicing | Public information; commercial access for detailed data |

These sources establish the difference between a software model of a robot and the actual parts needed to repair it.

![](https://www.google.com/s2/favicons?domain=https://support.unitree.com&sz=32)

support.unitree.com

+4

Particularly valuable discovery

# Unitree's model revisions

Unitree's published G1 descriptions distinguish robot configurations with different hip gear ratios, wrist motors, waist configurations and degrees of freedom. The documentation also identifies deprecated variants.

![](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

This is precisely why POW must index components against a particular robot revision, rather than simply saying that a part fits a G1.

A motor with the correct general description is not necessarily a valid replacement for a different G1 configuration.

Universal Robots is an equally useful research target for a different reason: its public service handbook includes joint replacement, torque values, fault diagnosis, brake testing, electrical drawings and post-replacement validation. That gives POW a model for structuring actual repair procedures, not just spare-parts listings.

![](https://www.google.com/s2/favicons?domain=https://www.universal-robots.com&sz=32)

Universal Robots

+1

For industrial robots, manufacturer-approved procedures and technicians must remain the authority for safety-critical repairs.


# 2. Open-source robot hardware: the fastest historical backfill

This is where I'd put considerable effort. Some robotics projects publish complete bills of materials, mechanical drawings, assembly instructions and even the tools needed to build them.

Start here

## Open Dynamic Robot Initiative

Max Planck and NYU open robotics project

Complete open hardware repository

It contains the Solo quadrupeds, Bolt biped, actuator designs, electronics, mechanical tools, consumables and step-by-step assembly and testing instructions.

Crucially, its actual bills of materials identify specific bearings, screws, inserts, motors, encoders and distributors. You can extract relationships between parts, robot assemblies and required workshop tools.

![](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+2

Other valuable sources are ROS Index and ROS distribution metadata for discovering robot description packages; ROBOTIS documentation for servomotor specifications and CAD; and Harmonic Drive for gearbox catalogues, STEP files and engineering drawings.

![](https://www.google.com/s2/favicons?domain=https://index.ros.org&sz=32)

ROS Index

+3

Harmonic Drive is particularly relevant to your robotics investment thesis. POW could record specifications and product changes for an important class of precision components while tracking the cost and availability of alternatives.

A critical distinction: a URDF or CAD model is evidence about mechanical configuration, not proof that a particular commercial replacement part fits a robot. Keep these relationships separate until verified.

# 3. Parts and supplier APIs

These are the structured data sources I'd integrate into `powphysical` and `powproducts`.

| Source | Available data | Integration |
| --- | --- | --- |
| Mouser | Component prices, stock, lead times, lifecycle and suggested replacements | API key |
| DigiKey | Component catalogue, pricing, availability and product-change notices | OAuth API |
| Farnell | UK electronic component catalogue, stock and prices | REST API key |
| Nexar | Multi-supplier component availability and supply-chain intelligence | GraphQL, registration |
| Harmonic Drive | Gearbox specifications and CAD | Downloadable documents |
| CubeMars | Robot actuators, technical specifications and listed prices | Public catalogue; no verified API |

Mouser documents a default allowance of 1,000 requests per day, enough for a carefully selected initial component watchlist. DigiKey and Farnell provide complementary regional and supplier information.

![](https://www.google.com/s2/favicons?domain=https://www.mouser.com&sz=32)

Mouser Electronics

+4

For Chinese sourcing, I'd initially maintain a catalogue of manufacturer-direct products, Alibaba and 1688 listings, and quoted supplier offers. I couldn't verify unrestricted production APIs for 1688 or AliExpress suitable for continuous commercial ingestion, so don't make them prerequisites for your first checkpoint.

The longer-term advantage is linking OEM replacement-part numbers to the upstream component manufacturer, then tracking regional prices and lead times. A dimensionally similar actuator should only be presented as a potential alternative until its electrical, mechanical, firmware and safety compatibility have been independently verified.


# 4. Repair knowledge, power tools and diagnostic equipment

I'd treat tools as first-class components of POW, rather than merely another product category. They form the connection between robot repair, ordinary electronics repair and your eventual marketplace.

| Source | What POW should extract |
| --- | --- |
| iFixit API | Repair steps, tools, fault descriptions and disassembly procedures |
| Bosch Professional | Exploded power-tool diagrams, replacement components and part numbers |
| DeWalt ServiceNet | Tool-model diagrams, spare parts and prices; check regional availability |
| Husqvarna Automower | Robotic mower parts, manuals, model revisions and troubleshooting |
| NASA Prognostics Repository | Bearing degradation, battery ageing and machinery failure datasets |

The iFixit API is particularly convenient: its guide endpoint supports filtering by repair type and fetching updates using `modifiedSince`. That makes it suitable for incremental collection rather than repeatedly fetching its entire catalogue. Check content licences before commercial reuse.

![](https://www.google.com/s2/favicons?domain=https://www.ifixit.com&sz=32)

iFixit

+1

Bosch publishes exploded diagrams covering 25 years of professional power tools in its UK catalogue. Its tool identifiers and replaceable assemblies offer a useful template for modelling the repair of equipment generally.

![](https://www.google.com/s2/favicons?domain=https://www.bosch-professional.com&sz=32)

Bosch Professional

+2

For specialist robot workshops, I'd build the tool catalogue around the following categories: precision torque drivers, ESD equipment, multimeters, oscilloscopes, bench power supplies, thermal cameras, bearing tools, crimpers, diagnostic interfaces, calibration equipment and lifting or supporting equipment.

A repair procedure should explicitly reference the tools it requires, their specifications and any applicable calibration requirements. This creates two commercial opportunities: recommending a verified tool to a technician and helping a business understand the cost of adding a new repair service.

NASA's failure datasets can support experimental diagnostic models, but they are not evidence of failure rates in particular commercially deployed robots. That dataset will ultimately have to come from real servicing records.

![](https://www.google.com/s2/favicons?domain=https://www.nasa.gov&sz=32)

NASA

+1

# 5. UK repair demand, technicians and contracts

The commercial data isn't just about equipment. You also need to know who owns robots, who maintains them and where servicing demand is emerging.

| Source | What to collect |
| --- | --- |
| Automate UK / BARA | Audited robot integrators and potential partners |
| Find a Tender API | Robotics, automation and maintenance tenders, awards and buyers |
| Contracts Finder API | Additional public contracts and historical procurement |
| Universal Robots Academy | Courses, servicing training and associated qualifications |
| UK product-safety alerts | Recalled and unsafe products requiring special handling |

Find a Tender offers structured OCDS data with incremental updates and historical procurement records. BARA's audited-integrator register and manufacturer training programmes provide an initial way to identify potential service partners.

![](https://www.google.com/s2/favicons?domain=https://www.find-tender.service.gov.uk&sz=32)

Find a Tender

+3

For a UK pilot, I would include industrial cobots and robotic lawnmowers alongside humanoids. Both already have established servicing ecosystems and publicly accessible maintenance documentation. Humanoids remain central to your research, but an existing service business offers a much clearer way to obtain verified repair outcomes.

UK HSE guidance also makes competence, safe isolation, stored-energy control and manufacturer maintenance instructions essential parts of servicing machinery. POW should distinguish informational repair guidance from work requiring qualified personnel.

![](https://www.google.com/s2/favicons?domain=https://www.hse.gov.uk&sz=32)

HSE

# 6. What the repositories should actually collect

## The shared POW repair graph

Robot model and revision

Manufacturer, model, variant, serial-number range, release dates and firmware compatibility.

Parts and assemblies

OEM numbers, component specifications, CAD, documented compatibility and replacement relationships.

Faults and procedures

Error codes, symptoms, manufacturer instructions, diagnostic observations and repair outcomes.

Suppliers and prices

UK, European and Chinese offers, stock, lead times, import costs and dated price history.

Tools and technicians

Required equipment, training, qualifications, service providers and workshop capabilities.

Verified servicing history

Actual failure → identified cause → parts purchased → repair performed → time and cost → validated result.

The last layer is the data moat. Manufacturer catalogues can be reproduced by other businesses with sufficient access. A growing, permissioned history of real repairs and verified outcomes is much harder to reconstruct.

For your current Layer 1 checkpoint, I'd assign work as follows:

1. `powrobots` — collect robot models, revisions, manufacturer documentation, CAD and component relationships. Start with Unitree, Universal Robots, ROBOTIS and open-source designs.

2. `repair` — collect servicing manuals, error codes, fault reports, required tools and repair procedures. Add technician-supplied outcomes once available.

3. `powproducts` and `powphysical` — build the component and tool catalogues, then ingest manufacturer pricing, distributor stock, supplier quotations and dated offers.

4. `powuk` — collect robotics tenders, integrators, technicians, qualifications and training providers.

Use `powops` to monitor each collector. Record the original source, retrieval timestamp, document revision, access rights, extracted fields and ingestion errors. Preserve raw observations before normalising them, and never silently overwrite earlier price or compatibility information.

I'd initially update official model and manual repositories daily or weekly, active supplier offers daily where permitted, and UK tenders according to their published update feeds. Historical repository releases and public procurement archives should be backfilled before prioritising sophisticated AI models.

The first milestone I'd target is one robot repairable on paper: its exact model revision, major replaceable assemblies, verified part numbers, manufacturer repair documentation, necessary tools, UK availability and sourced replacement costs. Complete that end to end and you'll have a working template for every subsequent robot.

That also gives you a concrete commercial test: approach a servicing business with one accurate, useful parts-and-repair dossier, rather than a large database whose practical accuracy has never been established.
