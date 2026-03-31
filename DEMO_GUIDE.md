# Transport ERP — Client Demo Guide

A step-by-step walkthrough to demonstrate the Transport & Logistics module to clients.

---

## Pre-Demo Setup (5 minutes)

```bash
# Start the system
docker compose up -d

# Wait until you see "Starting ERPNext..." in logs
docker compose logs -f erp-app

# Load demo data (realistic scenarios with 5 customers, 11 trips, fuel logs)
docker exec -it erp-app bench --site erp.localhost execute transport.demo.load

# To reset and start fresh anytime:
docker exec -it erp-app bench --site erp.localhost execute transport.demo.clear
docker exec -it erp-app bench --site erp.localhost execute transport.demo.load
```

**Login:** http://localhost:8000 → `Administrator` / `admin123`

---

## Demo Script

### Act 1: The Module Overview (2 minutes)

**Open:** http://localhost:8000/app/transport

> *"This is the Transport & Logistics module. Everything your operations team needs is organized here — from booking trips to tracking costs to running reports."*

Point out:
- **Quick action buttons** at the top (New Order, New Trip)
- **Operations** section (Transport Orders, Trips)
- **Master Data** (Trucks, Drivers, Routes)
- **Fuel & Costs** (Fuel Logs, Consumption reports)
- **Contracts** (Rate Cards with customer agreements)
- **Reports** (8 operational reports)

---

### Act 2: The Fleet (1 minute)

**Open:** http://localhost:8000/app/truck

> *"Here's our fleet. We track every truck — type, capacity, status. One truck is currently in maintenance for an engine overhaul."*

Click on **TRK-001-GP** to show:
- Vehicle details (Mercedes Actros, 30 tons)
- Dashboard connections — "See all trips for this truck"
- Status management (Active/Maintenance/Retired)

**Open:** http://localhost:8000/app/driver

> *"Our drivers — each assigned to a truck. The system tracks which driver did which trip."*

---

### Act 3: Customer Contracts (2 minutes)

**Open:** http://localhost:8000/app/transport-rate-card

> *"Before we start hauling, we set up rate agreements with each customer. These are locked-in rates per route."*

Click on any Rate Card to show:
- Customer + Route combination
- Rate type (Fixed per Trip / Per Km / Per Ton)
- Validity period
- **Key point:** *"When we book a trip, the system automatically pulls the correct rate — no manual entry, no mistakes."*

**Open:** http://localhost:8000/app/query-report/Rate%20Card%20Summary

> *"Management can see all contracts at a glance. Notice QuickMart's contract expires in 10 days — the system flags it."*

---

### Act 4: The Core Workflow — Order to Delivery (5 minutes)

#### Step 1: Customer calls with a job

**Open:** http://localhost:8000/app/transport-order

> *"A customer calls — they need cargo moved. We create a Transport Order."*

Show the existing orders, then **create a new one live:**
1. Click **+ Add Transport Order**
2. Customer: `Steelworks SA`
3. Pickup: `Steelworks Germiston Plant`
4. Delivery: `Durban Port Terminal 3`
5. Cargo: `Steel beams — 27 tons`
6. Weight: `27`
7. Save → **Submit** (Ctrl+Enter)

> *"Order confirmed. Now we book a trip."*

#### Step 2: Book the trip

Click **+ Add Trip** or navigate to http://localhost:8000/app/trip/new

1. Transport Order: Select the order you just created
2. **Customer auto-fills** from the order
3. Truck: `TRK-001-GP`
4. Driver: First driver in list
5. Route: `Johannesburg → Durban`
6. **Watch the revenue auto-populate:** R15,000 (from the Rate Card!)

> *"The system found the active rate card for Steelworks on this route and automatically set the revenue. No guessing."*

7. Add Planned Costs:
   | Cost Type | Amount |
   |---|---|
   | Diesel/Fuel | 3,500 |
   | Toll Fees | 850 |
   | Driver Allowance | 600 |

8. Save → Trip number auto-generated: **TRIP-000012**

> *"Trip planned. Total planned cost: R4,950. Expected profit: R10,050."*

#### Step 3: Start the trip

Click **Actions → Start Trip**

> *"The truck picks up the cargo. Status changes to In Progress. A 'Picked Up' checkpoint is automatically recorded with the timestamp."*

Show the **Trip Tracking** section — checkpoint is there.

#### Step 4: Track on the road

Click **Track → In Transit**
- Location: `N3 Highway — Harrismith`
- Notes: `Clear roads, good progress`

> *"Operations can track the truck at key waypoints. Every checkpoint is timestamped and logged."*

Click **Track → At Checkpoint**
- Location: `Van Reenen Pass weigh bridge`

#### Step 5: Record actual costs

Scroll to **Actual Costs** section and add:

| Cost Type | Actual Amount |
|---|---|
| Diesel/Fuel | 3,800 |
| Toll Fees | 850 |
| Driver Allowance | 600 |

Save → Show the **Cost Variance Analysis** section:

> *"Actual fuel was R300 over plan. The system calculates the variance automatically — 6.1% over budget on this trip."*

#### Step 6: Complete delivery

Click **Actions → Mark as Delivered**

> *"Delivered. The system records the delivery date, adds a 'Delivered' checkpoint, and calculates final profitability."*

**Show the profitability section:**
- Revenue: R15,000
- Total Cost: R5,250
- **Gross Profit: R9,750 (65%)**

#### Step 7: Invoice the customer

Click **Actions → Create Invoice**

> *"One click — the invoice is generated in ERPNext, linked to this trip. Finance can track payment from here."*

---

### Act 5: Show Existing Data — The Story (3 minutes)

**Open:** http://localhost:8000/app/trip

> *"Let me show you what a month of operations looks like."*

Point out the **status colors** on the list:
- Green = Completed
- Blue = In Progress
- Grey = Draft (scheduled)

#### The problem trip

Click on **Trip 3** (FreshCo, Durban to Cape Town):

> *"This trip had a tyre blowout. Look at the checkpoints — you can see exactly where and when the delay happened. And the actual costs include R4,500 in unexpected repairs. The system flagged it as Over Budget."*

Show:
- Checkpoints: Delayed at Mthatha, back on road 3 hours later
- Actual costs: Repairs R4,500 not in plan
- Budget status: **Over Budget by 40.7%**
- Still profitable though: R16,650 profit

#### The in-progress trips

Click on **Trip 8** (TechLog, on the road now):

> *"This truck is currently en route to Cape Town. You can see the last checkpoint — Beaufort West. ETA 6 hours."*

Click on **Trip 9** (AfriMine, at border):

> *"This one is at the Mozambique border in customs. Cross-border trips need permit tracking — it's all here."*

---

### Act 6: Reports & Analytics (3 minutes)

**Open:** http://localhost:8000/app/transport-dashboard

> *"The management dashboard — KPIs at a glance."*

Show: Total trips, active trips, revenue, cost, profit.

**Open:** http://localhost:8000/app/query-report/Truck%20Performance

> *"Which trucks make us the most money? TRK-001 is our star — 4 trips, highest profit. TRK-004 is underperforming — thin margins on the Bloemfontein route."*

**Open:** http://localhost:8000/app/query-report/Trip%20Cost%20vs%20Plan

> *"Where are we overspending? The bar chart shows planned vs actual side by side. The FreshCo trip stands out — that's the one with the tyre blowout."*

**Open:** http://localhost:8000/app/query-report/Route%20Profitability

> *"Which routes should we focus on? JHB-to-Cape Town and Pretoria-to-Maputo are our most profitable routes. Bloemfontein is barely breaking even."*

**Open:** http://localhost:8000/app/query-report/Fuel%20Consumption

> *"Fuel is our biggest cost. This shows consumption per truck. TRK-001 gets 2.6 km/liter — our most efficient. The refrigerated truck (TRK-003) burns more, as expected."*

**Open:** http://localhost:8000/app/query-report/Rate%20Card%20Summary

> *"Contract management — QuickMart's contract expires in 10 days. The system alerts us before we lose revenue."*

---

### Act 7: What Else Is Included (1 minute)

> *"This is built on ERPNext — so you also get, out of the box:"*

- **Sales & Invoicing** — full AR tracking
- **Finance & Accounting** — chart of accounts, GL, trial balance, P&L
- **Procurement** — for truck parts, fuel contracts
- **HR** — driver records, leave, payroll
- **CRM** — customer relationship management
- **Role-based Access** — Transport Manager sees everything, drivers see only their trips
- **Audit Trail** — every change is logged

---

## Demo Data Summary

| What | Count | Story |
|---|---|---|
| Trucks | 5 | 3 active performers, 1 average, 1 in maintenance |
| Drivers | 4 | Senior (John), Long-haul specialist (Peter), Cross-border (Sipho), New hire (David) |
| Routes | 5 | 4 domestic, 1 cross-border (Maputo) |
| Customers | 5 | Steel, Food, Tech, Mining, Retail |
| Rate Cards | 5 | Fixed, Per-Km, Per-Ton rates + 1 expiring soon |
| Completed Trips | 7 | Mix of profitable, over-budget, thin margin |
| In Progress Trips | 2 | One on highway, one at border crossing |
| Draft Trips | 2 | Scheduled for tomorrow and next week |
| Fuel Logs | 11 | Consumption patterns per truck |

### Key Numbers That Tell the Story

| Metric | Value |
|---|---|
| Total Revenue (completed) | ~R157,300 |
| Total Cost (completed) | ~R62,600 |
| Average Profit Margin | ~60% |
| Over-budget trip | Trip 3 (FreshCo) — tyre blowout, +40% over plan |
| Most profitable route | JHB → Cape Town (R32K per trip) |
| Least profitable | JHB → Bloemfontein (R2,800 profit, 43% margin) |
| Most efficient truck | TRK-001-GP (Mercedes) — 2.6 km/liter |
| Expiring contract | QuickMart — 10 days left |

---

## Quick Reference — Key URLs

| Page | URL |
|---|---|
| Transport Module | /app/transport |
| Trip List | /app/trip |
| Transport Orders | /app/transport-order |
| Trucks | /app/truck |
| Drivers | /app/driver |
| Routes | /app/route |
| Fuel Logs | /app/fuel-log |
| Rate Cards | /app/transport-rate-card |
| Dashboard | /app/transport-dashboard |
| Trip Register | /app/query-report/Trip%20Register |
| Cost vs Plan | /app/query-report/Trip%20Cost%20vs%20Plan |
| Profit per Trip | /app/query-report/Profit%20per%20Trip |
| Truck Performance | /app/query-report/Truck%20Performance |
| Route Profitability | /app/query-report/Route%20Profitability |
| Fuel Consumption | /app/query-report/Fuel%20Consumption |
| Rate Card Summary | /app/query-report/Rate%20Card%20Summary |
