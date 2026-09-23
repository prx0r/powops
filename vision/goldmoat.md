# The Gold Moat: graph + product + outcome data flywheel

**Core thesis:** The durable competitive advantage is not any single product or dataset. It is the feedback loop between a growing procurement intelligence graph and physical products that generate outcome data no competitor can scrape.

---

## The flywheel

```
POW PROCUREMENT GRAPH
  knows which parts robots need
  knows which suppliers deliver
  knows UK landed costs
          ↓
CONSUMER PHYSICAL PRODUCTS
  plant agents, desk agents, pet agents
  sold through Etsy / direct
  personalised, narrow-niche, £15-40 BOM
          ↓
OUTCOME DATA (the moat)
  which sensors actually fail in the field
  which connectors corrode after 6 months
  which enclosure designs get returned
  which provisioning flows cause support tickets
  which price points actually convert
  which personalisation options customers pay extra for
          ↓
FEEDS BACK INTO GRAPH
  more reliable quotations
  better BOM recommendations
  accurate failure-rate predictions
  verified supplier quality scores
  component-cost-trend detection
          ↓
BETTER PRODUCTS
  cheaper, more reliable, more varied
  new categories become viable when costs cross thresholds
          ↓
MORE OUTCOME DATA
```

Nobody else has this loop. JLCPCB has fabrication. iRobot has parts. Etsy has sellers. 1clickBOM fills carts. But none of them join procurement intelligence to physical product outcomes to a growing compatibility graph.

---

## Why this is hard to copy

**The graph alone is scrapable.** Anyone can build a price comparison site. But a price comparison site doesn't know which parts actually work together in the field.

**The product alone is copyable.** Anyone can list plant gadgets on Etsy. But a generic plant gadget seller doesn't know which sensor combinations are most reliable at the lowest cost, because they don't have transaction-level outcome data from thousands of units.

**The combination is the moat.** The graph makes the product better. The product generates data the graph can't get any other way. Every transaction strengthens both sides. A competitor would need to build the graph AND sell the products AND accumulate the outcome data — simultaneously — while you're already two years into the loop.

---

## The three layers

### Layer 1: Procurement graph (powvision)
- Robot model → exact revision → verified BOM → compatible alternatives → suppliers → UK landed cost
- Covers: robot vacuums, open-source arms (SO-101), robotic lawnmowers, hobby electronics
- Sources: manufacturer docs, LCSC API, JLCPCB API, iFixit, open hardware repos
- Moat: verified compatibility + transaction outcomes accumulating over time

### Layer 2: Consumer physical agents (robotprintify)
- Single-purpose physical agents with personality + sensors + actuators
- Categories: plant, desk, pet, ambient, wellness, maker/collector
- One reusable core board (POW Agent Node) powers all categories
- Personalised on Etsy: "made for Sarah and her monstera"
- BOM: £15-40 (ESP32 + sensors + LED + enclosure)

### Layer 3: Outcome data (the gold)
- Return rates by component type
- Failure modes by supplier and batch
- Assembly time by configuration
- Customer willingness-to-pay by personalisation option
- Actual delivery times by supplier and destination
- Which configurations recur → custom PCB candidates

---

## The consumer product platform

### POW Agent Node (one board, many products)

```
ESP32-S3
USB-C
Wi-Fi/BLE
mic
speaker output
RGB LED
I2C
GPIO
servo output
sensor ports
```

Different peripherals + enclosures = different products:

```
Agent Node
├── Plant agent (moisture + light + temp + pump relay)
├── Desk agent (button + knob + display + status light)
├── Pet agent (camera + speaker + treat dispenser)
├── Lamp agent (RGB + dimmer + schedule)
├── Speaker agent (audio output + mic + rotary)
├── Camera agent (ESP3-CAM + pan/tilt servo)
└── Tiny robot (wheels + ultrasonic + servo head)
```

### POW Motion Node
```
CAN bus
2-4 motors
encoders
current sensing
servo outputs
```

### POW Power Node
```
battery + charging
DC/DC conversion
BMS
power monitoring
```

Three boards construct most consumer physical-agent products.

---

## The product progression

```
POW observes cheap primitives
        ↓
detect viable product configuration
        ↓
prototype with commodity modules
        ↓
sell 10-50 through Etsy
        ↓
observe actual demand/failures
        ↓
integrate repeated configuration
        ↓
custom PCB / enclosure
        ↓
spin out tiny brand
```

Each step generates data that strengthens the graph. The Etsy products are probes into the graph, not the end goal.

---

## The "what became possible" query

The most valuable derived feed from the graph:

> **"What new $20 / $50 / $100 physical-agent products became possible this month because component costs crossed a threshold?"**

This is only possible if you track:
- ESP32 pricing trends over time
- Sensor module cost curves
- Motor/actuator price changes
- Battery pricing
- Fabrication quotes (JLCPCB, PCBWay)
- Enclosure material costs

When a combination drops below a price point, a new product category becomes viable. That's a product-discovery engine nobody else can run.

---

## Build order

### Phase 1: Graph foundation (months 1-2)
- 10 robot vacuum models + 2-3 open-source arms (SO-101)
- Exact BOMs, verified parts, 2+ supplier quotes each
- LCSC integration for electronic components
- UK landed-cost model with VAT/duty/shipping
- First 5 "opportunity cards" manually verified

### Phase 2: First product probe (months 2-3)
- Build POW Agent Node prototype
- Plant agent as first product (cheapest BOM, clearest value prop)
- Personalised enclosure + software
- List on Etsy, 10-50 units
- Record every failure, return, support question

### Phase 3: Feedback loop (months 3-4)
- Feed outcome data back into graph
- Adjust component choices based on real failure rates
- Build second product (desk agent or pet agent)
- Test pricing: £29 / £49 / £79

### Phase 4: Scale the graph (months 4-6)
- Add robotic lawnmower models (Husqvarna, Gardena)
- Add more open-source designs (LeRobot, AR4)
- Integrate JLCPCB fabrication quotes
- Build procurement API (model → verified basket → order)
- First paying API customers (repair shops, small manufacturers)

### Phase 5: Scale the products (months 6-12)
- Custom PCB for Agent Node (volume reduces cost)
- 3-5 product lines on Etsy
- Custom brand storefront
- First wholesale / B2B orders
- Agent SDK for Muse/ChatGPT integration

---

## The compounding math

Year 1 (months 1-12):
- 500 units sold × £35 contribution = £17,500
- Graph covers 50 robots, 500 parts, 20 suppliers
- 500 outcome data points (failures, returns, assembly times)

Year 2:
- 2,000 units sold × £35 contribution = £70,000
- Graph covers 200 robots, 2,000 parts, 50 suppliers
- 2,500 outcome data points
- API customers paying £49-299/month
- Custom PCB reduces BOM by 30%

Year 3:
- 5,000 units × £40 (volume margin) = £200,000
- API revenue: £50,000/year
- Graph is the defensible asset
- Outcome data makes quotations 3x more accurate than any competitor
- New product categories discovered automatically by cost-threshold detection

The revenue grows, but the graph + outcome data grows faster. That's the moat.

---

## What this is NOT

- NOT a general-purpose home robot (too hard, too expensive, too early)
- NOT an electronics distributor (RS/Farnell/Mouser already won that)
- NOT a Shopify scraper (thin moat, anyone can copy)
- NOT a trades marketplace (too early, no differentiation yet)
- NOT an AI agent company (AI is a feature, not the product)

## What this IS

- A procurement intelligence graph for physical robotics
- A consumer product platform that generates outcome data
- A compounding feedback loop between the two
- A future API for AI agents that need to source and build physical objects

The product is the probe. The graph is the asset. The outcome data is the moat.
