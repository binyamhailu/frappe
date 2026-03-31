# Transport ERP - POC

ERPNext-based ERP with a custom Transport & Logistics module for trip-based operations.

## Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ RAM available
- Ports 8000, 9000, 3307 free

### One-Command Setup

```bash
docker compose up --build
```

First run takes ~10-15 minutes (downloading images, building, installing ERPNext).
Subsequent runs take ~30 seconds.

### Access

Once you see `Starting ERPNext...` in the logs:

| | |
|---|---|
| **URL** | http://localhost:8000 |
| **Username** | Administrator |
| **Password** | admin123 |

### Key Pages

| Page | URL |
|---|---|
| Trip List | http://localhost:8000/app/trip |
| Transport Orders | http://localhost:8000/app/transport-order |
| Trucks | http://localhost:8000/app/truck |
| Drivers | http://localhost:8000/app/driver |
| Routes | http://localhost:8000/app/route |
| Dashboard | http://localhost:8000/app/transport-dashboard |
| Trip Register | http://localhost:8000/app/query-report/Trip%20Register |
| Cost vs Plan | http://localhost:8000/app/query-report/Trip%20Cost%20vs%20Plan |
| Profit per Trip | http://localhost:8000/app/query-report/Profit%20per%20Trip |
| Truck Performance | http://localhost:8000/app/query-report/Truck%20Performance |
| Cost Breakdown | http://localhost:8000/app/query-report/Cost%20Breakdown%20by%20Category |
| Route Profitability | http://localhost:8000/app/query-report/Route%20Profitability |

## Demo Workflow

### End-to-End Trip Lifecycle:

1. **Create Transport Order** - `/app/transport-order/new`
   - Select customer, pickup/delivery locations, cargo details
   - Submit the order

2. **Book a Trip** - `/app/trip/new`
   - Link to transport order, assign truck + driver + route
   - Enter planned costs (fuel, tolls, permits, etc.)
   - Set revenue (transport fee)

3. **Start Trip** - Click "Actions > Start Trip"
   - Status changes to In Progress
   - Actual start date is recorded

4. **Record Actual Costs** - Edit the trip
   - Enter actual costs in the Actual Costs table
   - System auto-calculates variance vs planned

5. **Complete Trip** - Click "Actions > Mark as Delivered"
   - Status changes to Completed
   - Delivery date recorded

6. **Create Invoice** - Click "Actions > Create Invoice"
   - Generates ERPNext Sales Invoice linked to the trip

7. **Close Trip** - Click "Actions > Close Trip"
   - Locks the trip from further edits

8. **View Reports** - Check dashboards and reports for analysis

## Transport Module Features

- Auto-increment trip numbers (TRIP-000001)
- Planned vs Actual cost tracking with variance analysis
- Budget status indicators (Over/Under Budget)
- Per-trip profitability (Revenue - Cost = Profit)
- Truck performance tracking
- Route profitability analysis
- 6 built-in reports with charts
- Full audit trail

## Standard ERPNext Modules Included

Sales, Procurement, Inventory, Finance/Accounting, HR, CRM, Projects, Workflows, Role-based Access Control

## Stop / Reset

```bash
# Stop
docker compose down

# Stop and delete all data (fresh start)
docker compose down -v
```

## Project Structure

```
erp/
├── docker-compose.yml      # One-click deployment
├── Dockerfile              # ERPNext + Transport build
├── entrypoint.sh           # Auto-setup script
├── mariadb.cnf             # MariaDB config
├── setup_site.py           # Demo data loader
└── apps/
    └── transport/          # Custom Transport module
        └── transport/
            └── transport/
                ├── doctype/
                │   ├── truck/
                │   ├── driver/
                │   ├── route/
                │   ├── transport_order/
                │   ├── trip/
                │   ├── trip_planned_cost/
                │   └── trip_actual_cost/
                ├── report/
                │   ├── trip_register/
                │   ├── trip_cost_vs_plan/
                │   ├── profit_per_trip/
                │   ├── truck_performance/
                │   ├── cost_breakdown_by_category/
                │   └── route_profitability/
                └── page/
                    └── transport_dashboard/
```
