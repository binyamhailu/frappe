"""
Transport Module — Demo Data Loader

Creates a realistic dataset that tells a compelling business story:
- 5 trucks (3 profitable, 1 average, 1 underperforming)
- 4 drivers with varying performance
- 5 routes (domestic + cross-border)
- 5 customers with rate cards
- 10 transport orders with 12 trips across different statuses
- Fuel logs showing consumption patterns
- Checkpoints showing trip tracking

Usage:
    bench --site erp.localhost execute transport.demo.load

To reset and reload:
    bench --site erp.localhost execute transport.demo.clear
    bench --site erp.localhost execute transport.demo.load
"""
import frappe
from frappe.utils import add_days, today, now_datetime, add_to_date


def load():
    """Load complete demo data. Safe to run multiple times."""
    frappe.set_user("Administrator")

    print("\n========================================")
    print("  Loading Transport Demo Data...")
    print("========================================\n")

    _ensure_fixtures()
    _create_trucks()
    _create_drivers()
    _create_routes()
    _create_customers()
    _create_rate_cards()
    _create_orders_and_trips()
    _create_fuel_logs()

    frappe.db.commit()

    # Print summary
    print("\n========================================")
    print("  DEMO DATA LOADED")
    print("========================================")
    print(f"  Trucks:           {frappe.db.count('Truck')}")
    print(f"  Drivers:          {frappe.db.count('Driver')}")
    print(f"  Routes:           {frappe.db.count('Route')}")
    print(f"  Customers:        {frappe.db.count('Customer')}")
    print(f"  Rate Cards:       {frappe.db.count('Transport Rate Card')}")
    print(f"  Transport Orders: {frappe.db.count('Transport Order')}")
    print(f"  Trips:            {frappe.db.count('Trip')}")
    print(f"  Fuel Logs:        {frappe.db.count('Fuel Log')}")
    print("========================================")
    print(f"  Open: http://localhost:8000/app/transport")
    print("========================================\n")


def clear():
    """Clear all transport demo data. Use before reload."""
    frappe.set_user("Administrator")
    print("Clearing transport data...")

    for dt in ["Fuel Log", "Trip"]:
        for d in frappe.get_all(dt):
            frappe.delete_doc(dt, d.name, force=True, ignore_permissions=True)

    for d in frappe.get_all("Transport Order", filters={"docstatus": ["!=", 2]}):
        doc = frappe.get_doc("Transport Order", d.name)
        if doc.docstatus == 1:
            doc.flags.ignore_permissions = True
            doc.cancel()
        frappe.delete_doc("Transport Order", d.name, force=True, ignore_permissions=True)

    for dt in ["Transport Rate Card", "Truck", "Driver", "Route"]:
        for d in frappe.get_all(dt):
            frappe.delete_doc(dt, d.name, force=True, ignore_permissions=True)

    frappe.db.commit()
    print("All transport data cleared.\n")


def _ensure_fixtures():
    """Create basic ERPNext fixtures if missing."""
    for wt in ["Transit", "Store"]:
        if not frappe.db.exists("Warehouse Type", wt):
            frappe.get_doc({"doctype": "Warehouse Type", "name": wt}).insert(ignore_permissions=True)

    if not frappe.db.exists("Customer Group", "All Customer Groups"):
        frappe.get_doc({"doctype": "Customer Group", "customer_group_name": "All Customer Groups", "is_group": 1}).insert(ignore_permissions=True)

    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({"doctype": "Territory", "territory_name": "All Territories", "is_group": 1}).insert(ignore_permissions=True)

    if not frappe.db.exists("Supplier Group", "All Supplier Groups"):
        frappe.get_doc({"doctype": "Supplier Group", "supplier_group_name": "All Supplier Groups", "is_group": 1}).insert(ignore_permissions=True)

    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "All Item Groups", "is_group": 1}).insert(ignore_permissions=True)

    if not frappe.db.exists("Item Group", "Services"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Services", "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True)

    for uom in ["Nos", "Kg", "Km", "Liter"]:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

    if not frappe.db.exists("Company", "Transport Co"):
        frappe.get_doc({
            "doctype": "Company", "company_name": "Transport Co", "abbr": "TC",
            "default_currency": "USD", "country": "South Africa", "enable_perpetual_inventory": 0,
        }).insert(ignore_permissions=True)

    frappe.defaults.set_global_default("company", "Transport Co")
    frappe.defaults.set_global_default("currency", "USD")
    frappe.db.commit()
    print("  [OK] Fixtures")


# ──────────────────────────────────────────────
# MASTER DATA
# ──────────────────────────────────────────────

def _create_trucks():
    trucks = [
        {"registration_number": "TRK-001-GP", "truck_type": "Flatbed", "capacity_tons": 30,
         "make": "Mercedes", "model": "Actros 2645", "year": 2023, "status": "Active"},
        {"registration_number": "TRK-002-GP", "truck_type": "Container", "capacity_tons": 28,
         "make": "Volvo", "model": "FH16 540", "year": 2024, "status": "Active"},
        {"registration_number": "TRK-003-KZN", "truck_type": "Refrigerated", "capacity_tons": 22,
         "make": "Scania", "model": "R500", "year": 2022, "status": "Active"},
        {"registration_number": "TRK-004-WC", "truck_type": "Tanker", "capacity_tons": 25,
         "make": "MAN", "model": "TGX 26.540", "year": 2021, "status": "Active"},
        {"registration_number": "TRK-005-GP", "truck_type": "Flatbed", "capacity_tons": 34,
         "make": "Mercedes", "model": "Actros 2652", "year": 2020, "status": "Maintenance",
         "notes": "Engine overhaul — expected back in service next week"},
    ]
    for t in trucks:
        if not frappe.db.exists("Truck", t["registration_number"]):
            frappe.get_doc({"doctype": "Truck", **t}).insert(ignore_permissions=True)
    print("  [OK] 5 Trucks (3 active high-performers, 1 average, 1 in maintenance)")


def _create_drivers():
    drivers = [
        {"driver_name": "John Mokoena", "license_number": "LIC-2024-001", "phone": "+27821234567",
         "assigned_truck": "TRK-001-GP", "notes": "Senior driver — 12 years experience, excellent fuel efficiency"},
        {"driver_name": "Peter Nkosi", "license_number": "LIC-2024-002", "phone": "+27829876543",
         "assigned_truck": "TRK-002-GP", "notes": "Specialist in long-haul Cape Town routes"},
        {"driver_name": "Sipho Dlamini", "license_number": "LIC-2024-003", "phone": "+27831112222",
         "assigned_truck": "TRK-003-KZN", "notes": "Cross-border certified — Mozambique, Swaziland"},
        {"driver_name": "David Mabena", "license_number": "LIC-2024-004", "phone": "+27845556666",
         "assigned_truck": "TRK-004-WC", "notes": "New hire — 6 months with company, still training on routes"},
    ]
    for d in drivers:
        if not frappe.db.exists("Driver", {"license_number": d["license_number"]}):
            frappe.get_doc({"doctype": "Driver", "status": "Active", **d}).insert(ignore_permissions=True)
    print("  [OK] 4 Drivers (mixed experience levels)")


def _create_routes():
    routes = [
        {"origin": "Johannesburg", "destination": "Durban", "estimated_distance_km": 580, "estimated_time_hours": 6.5},
        {"origin": "Johannesburg", "destination": "Cape Town", "estimated_distance_km": 1400, "estimated_time_hours": 14},
        {"origin": "Durban", "destination": "Cape Town", "estimated_distance_km": 1650, "estimated_time_hours": 17},
        {"origin": "Pretoria", "destination": "Maputo", "estimated_distance_km": 560, "estimated_time_hours": 7,
         "notes": "Cross-border — requires Mozambique transit permit"},
        {"origin": "Johannesburg", "destination": "Bloemfontein", "estimated_distance_km": 400, "estimated_time_hours": 4.5},
    ]
    for r in routes:
        rname = f"{r['origin']} \u2192 {r['destination']}"
        if not frappe.db.exists("Route", rname):
            frappe.get_doc({"doctype": "Route", **r}).insert(ignore_permissions=True)
    print("  [OK] 5 Routes (4 domestic, 1 cross-border)")


def _create_customers():
    customers = [
        ("Steelworks SA", "Major steel manufacturer — high volume, reliable payment"),
        ("FreshCo Foods", "Perishable goods — time-sensitive, refrigerated"),
        ("TechLog Distribution", "Electronics — high value cargo, requires careful handling"),
        ("AfriMine Resources", "Mining equipment — heavy loads, cross-border"),
        ("QuickMart Retail", "Retail distribution — frequent small loads, thin margins"),
    ]
    for cname, notes in customers:
        if not frappe.db.exists("Customer", cname):
            frappe.get_doc({
                "doctype": "Customer", "customer_name": cname, "customer_type": "Company",
                "customer_group": "All Customer Groups", "territory": "All Territories",
            }).insert(ignore_permissions=True)
    print("  [OK] 5 Customers (diverse industries)")


def _create_rate_cards():
    if frappe.db.count("Transport Rate Card") > 0:
        return

    cards = [
        # High-margin routes
        {"customer": "Steelworks SA", "route": "Johannesburg \u2192 Durban",
         "rate_type": "Fixed per Trip", "rate_per_trip": 15000,
         "effective_from": add_days(today(), -180), "effective_to": add_days(today(), 180)},
        {"customer": "TechLog Distribution", "route": "Johannesburg \u2192 Cape Town",
         "rate_type": "Fixed per Trip", "rate_per_trip": 32000,
         "effective_from": add_days(today(), -90), "effective_to": add_days(today(), 90)},
        # Per-km rate
        {"customer": "FreshCo Foods", "route": "Durban \u2192 Cape Town",
         "rate_type": "Per Km", "rate_per_km": 22,
         "effective_from": add_days(today(), -60), "effective_to": add_days(today(), 120)},
        # Cross-border — premium
        {"customer": "AfriMine Resources", "route": "Pretoria \u2192 Maputo",
         "rate_type": "Per Ton", "rate_per_ton": 1400,
         "effective_from": add_days(today(), -45), "effective_to": add_days(today(), 135)},
        # Thin margin — expiring soon
        {"customer": "QuickMart Retail", "route": "Johannesburg \u2192 Bloemfontein",
         "rate_type": "Fixed per Trip", "rate_per_trip": 6500,
         "effective_from": add_days(today(), -150), "effective_to": add_days(today(), 10),
         "notes": "Contract up for renewal — client requesting 5% discount"},
    ]
    for c in cards:
        frappe.get_doc({"doctype": "Transport Rate Card", "status": "Active", **c}).insert(ignore_permissions=True)
    print("  [OK] 5 Rate Cards (3 healthy, 1 premium, 1 expiring soon)")


# ──────────────────────────────────────────────
# OPERATIONAL DATA — THE STORY
# ──────────────────────────────────────────────

def _create_orders_and_trips():
    if frappe.db.count("Trip") > 0:
        print("  [--] Trips exist, skipping...")
        return

    drivers = [d.name for d in frappe.get_all("Driver", fields=["name"], order_by="creation")]

    # ── STORY: 10 orders, 12 trips across various states ──

    scenarios = [
        # ── COMPLETED TRIPS (the backbone — show history) ──
        {
            "label": "Trip 1: Steelworks — JHB to Durban (profitable, on time)",
            "order": {"customer": "Steelworks SA", "order_date": add_days(today(), -21),
                      "pickup_location": "Steelworks SA — Germiston Plant",
                      "delivery_location": "Durban Port — Terminal 2",
                      "cargo_description": "Hot-rolled steel coils — 28 tons", "weight": 28,
                      "requested_delivery_date": add_days(today(), -19)},
            "trip": {"truck": "TRK-001-GP", "driver": drivers[0],
                     "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": add_days(today(), -21),
                     "planned_end_date": add_days(today(), -20),
                     "revenue": 15000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 850},
                         {"cost_type": "Driver Allowance", "planned_amount": 600},
                         {"cost_type": "Permits", "planned_amount": 150},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 3200},
                         {"cost_type": "Toll Fees", "actual_amount": 850},
                         {"cost_type": "Driver Allowance", "actual_amount": 600},
                         {"cost_type": "Permits", "actual_amount": 150},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -21), "Germiston Plant", "Loaded 28 tons steel coils"),
                ("In Transit", add_days(today(), -21), "N3 Highway — Harrismith", "Clear roads"),
                ("Arrived at Destination", add_days(today(), -20), "Durban Port Gate", "Waiting for dock slot"),
                ("Delivered", add_days(today(), -20), "Durban Port Terminal 2", "Offloaded — POD signed"),
            ],
        },
        {
            "label": "Trip 2: TechLog — JHB to Cape Town (high value, under budget)",
            "order": {"customer": "TechLog Distribution", "order_date": add_days(today(), -18),
                      "pickup_location": "TechLog Warehouse — Midrand",
                      "delivery_location": "Cape Town Distribution Centre — Epping",
                      "cargo_description": "Server equipment & networking gear — 12 tons", "weight": 12,
                      "requested_delivery_date": add_days(today(), -15)},
            "trip": {"truck": "TRK-002-GP", "driver": drivers[1],
                     "route": "Johannesburg \u2192 Cape Town",
                     "planned_start_date": add_days(today(), -18),
                     "planned_end_date": add_days(today(), -16),
                     "revenue": 32000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 8500},
                         {"cost_type": "Toll Fees", "planned_amount": 1600},
                         {"cost_type": "Driver Allowance", "planned_amount": 1500},
                         {"cost_type": "Permits", "planned_amount": 200},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 7800},
                         {"cost_type": "Toll Fees", "actual_amount": 1550},
                         {"cost_type": "Driver Allowance", "actual_amount": 1500},
                         {"cost_type": "Permits", "actual_amount": 200},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -18), "TechLog Midrand", "High-value cargo sealed"),
                ("In Transit", add_days(today(), -18), "N1 — Bloemfontein", "Overnight stop"),
                ("In Transit", add_days(today(), -17), "N1 — Beaufort West", "Good progress"),
                ("Arrived at Destination", add_days(today(), -16), "Cape Town Epping", "At DC gate"),
                ("Delivered", add_days(today(), -16), "Cape Town DC — Bay 4", "Cargo inspected, all items intact"),
            ],
        },
        {
            "label": "Trip 3: FreshCo — Durban to Cape Town (OVER BUDGET — repairs)",
            "order": {"customer": "FreshCo Foods", "order_date": add_days(today(), -14),
                      "pickup_location": "FreshCo Cold Store — Durban North",
                      "delivery_location": "FreshCo Cape Town — Philippi",
                      "cargo_description": "Frozen foods & dairy — 20 tons (refrigerated)", "weight": 20,
                      "requested_delivery_date": add_days(today(), -11)},
            "trip": {"truck": "TRK-003-KZN", "driver": drivers[2],
                     "route": "Durban \u2192 Cape Town",
                     "planned_start_date": add_days(today(), -14),
                     "planned_end_date": add_days(today(), -12),
                     "revenue": 36300,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 10000},
                         {"cost_type": "Toll Fees", "planned_amount": 1900},
                         {"cost_type": "Driver Allowance", "planned_amount": 1800},
                         {"cost_type": "Permits", "planned_amount": 250},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 11200},
                         {"cost_type": "Toll Fees", "actual_amount": 1900},
                         {"cost_type": "Driver Allowance", "actual_amount": 1800},
                         {"cost_type": "Repairs", "actual_amount": 4500},
                         {"cost_type": "Permits", "actual_amount": 250},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -14), "FreshCo Durban", "Refrigeration unit at -18C"),
                ("In Transit", add_days(today(), -14), "N2 — Port Shepstone", "Normal"),
                ("Delayed", add_days(today(), -13), "N2 — Mthatha", "Tyre blowout — replacing"),
                ("In Transit", add_days(today(), -13), "N2 — East London", "Back on road, 3hr delay"),
                ("Delivered", add_days(today(), -11), "FreshCo Cape Town", "Delivered late — client notified"),
            ],
        },
        {
            "label": "Trip 4: AfriMine — Pretoria to Maputo (cross-border, high margin)",
            "order": {"customer": "AfriMine Resources", "order_date": add_days(today(), -12),
                      "pickup_location": "AfriMine Depot — Pretoria West",
                      "delivery_location": "Maputo Port — Cargo Terminal",
                      "cargo_description": "Mining drill components — 18 tons", "weight": 18,
                      "requested_delivery_date": add_days(today(), -10)},
            "trip": {"truck": "TRK-001-GP", "driver": drivers[2],
                     "route": "Pretoria \u2192 Maputo",
                     "planned_start_date": add_days(today(), -12),
                     "planned_end_date": add_days(today(), -11),
                     "revenue": 25200,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3800},
                         {"cost_type": "Toll Fees", "planned_amount": 600},
                         {"cost_type": "Permits", "planned_amount": 2200},
                         {"cost_type": "Driver Allowance", "planned_amount": 1000},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 3900},
                         {"cost_type": "Toll Fees", "actual_amount": 650},
                         {"cost_type": "Permits", "actual_amount": 2200},
                         {"cost_type": "Driver Allowance", "actual_amount": 1000},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -12), "AfriMine Pretoria", "Loaded drilling equipment"),
                ("In Transit", add_days(today(), -12), "N4 — Nelspruit", "Approaching border"),
                ("At Border", add_days(today(), -12), "Lebombo/Ressano Garcia", "Customs clearance — 2hr wait"),
                ("In Transit", add_days(today(), -11), "EN1 — Mozambique", "Clear road"),
                ("Delivered", add_days(today(), -11), "Maputo Port", "Delivered on time"),
            ],
        },
        {
            "label": "Trip 5: Steelworks — JHB to Durban #2 (repeat customer)",
            "order": {"customer": "Steelworks SA", "order_date": add_days(today(), -9),
                      "pickup_location": "Steelworks SA — Germiston Plant",
                      "delivery_location": "Durban Port — Terminal 1",
                      "cargo_description": "Steel reinforcement bars — 30 tons", "weight": 30,
                      "requested_delivery_date": add_days(today(), -7)},
            "trip": {"truck": "TRK-001-GP", "driver": drivers[0],
                     "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": add_days(today(), -9),
                     "planned_end_date": add_days(today(), -8),
                     "revenue": 15000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 850},
                         {"cost_type": "Driver Allowance", "planned_amount": 600},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 3350},
                         {"cost_type": "Toll Fees", "actual_amount": 850},
                         {"cost_type": "Driver Allowance", "actual_amount": 600},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -9), "Germiston Plant", "Loaded"),
                ("Delivered", add_days(today(), -8), "Durban Port T1", "On time"),
            ],
        },
        {
            "label": "Trip 6: QuickMart — JHB to Bloem (thin margin)",
            "order": {"customer": "QuickMart Retail", "order_date": add_days(today(), -7),
                      "pickup_location": "QuickMart DC — Kempton Park",
                      "delivery_location": "QuickMart Bloemfontein Store",
                      "cargo_description": "Mixed retail goods — 15 tons", "weight": 15,
                      "requested_delivery_date": add_days(today(), -6)},
            "trip": {"truck": "TRK-004-WC", "driver": drivers[3],
                     "route": "Johannesburg \u2192 Bloemfontein",
                     "planned_start_date": add_days(today(), -7),
                     "planned_end_date": add_days(today(), -6),
                     "revenue": 6500,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 2400},
                         {"cost_type": "Toll Fees", "planned_amount": 500},
                         {"cost_type": "Driver Allowance", "planned_amount": 400},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 2800},
                         {"cost_type": "Toll Fees", "actual_amount": 500},
                         {"cost_type": "Driver Allowance", "actual_amount": 400},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -7), "Kempton Park DC", "Loaded"),
                ("Delivered", add_days(today(), -6), "Bloemfontein Store", "On time"),
            ],
        },
        {
            "label": "Trip 7: QuickMart — JHB to Bloem #2 (thin margin, repeat)",
            "order": {"customer": "QuickMart Retail", "order_date": add_days(today(), -4),
                      "pickup_location": "QuickMart DC — Kempton Park",
                      "delivery_location": "QuickMart Bloemfontein Store",
                      "cargo_description": "Household goods — 14 tons", "weight": 14,
                      "requested_delivery_date": add_days(today(), -3)},
            "trip": {"truck": "TRK-004-WC", "driver": drivers[3],
                     "route": "Johannesburg \u2192 Bloemfontein",
                     "planned_start_date": add_days(today(), -4),
                     "planned_end_date": add_days(today(), -3),
                     "revenue": 6500,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 2400},
                         {"cost_type": "Toll Fees", "planned_amount": 500},
                         {"cost_type": "Driver Allowance", "planned_amount": 400},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 2650},
                         {"cost_type": "Toll Fees", "actual_amount": 500},
                         {"cost_type": "Driver Allowance", "actual_amount": 400},
                     ]},
            "action": "complete",
            "checkpoints": [
                ("Picked Up", add_days(today(), -4), "Kempton Park DC", "Loaded"),
                ("Delivered", add_days(today(), -3), "Bloemfontein Store", "On time"),
            ],
        },

        # ── IN PROGRESS TRIPS (show live tracking) ──
        {
            "label": "Trip 8: TechLog — JHB to Cape Town (IN PROGRESS — on the road now)",
            "order": {"customer": "TechLog Distribution", "order_date": add_days(today(), -2),
                      "pickup_location": "TechLog Warehouse — Midrand",
                      "delivery_location": "Cape Town DC — Epping",
                      "cargo_description": "Laptops & monitors — 8 tons (high value)", "weight": 8,
                      "requested_delivery_date": add_days(today(), 1)},
            "trip": {"truck": "TRK-002-GP", "driver": drivers[1],
                     "route": "Johannesburg \u2192 Cape Town",
                     "planned_start_date": add_days(today(), -2),
                     "planned_end_date": today(),
                     "revenue": 32000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 8500},
                         {"cost_type": "Toll Fees", "planned_amount": 1600},
                         {"cost_type": "Driver Allowance", "planned_amount": 1500},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 4200},
                     ]},
            "action": "start",
            "checkpoints": [
                ("Picked Up", add_days(today(), -2), "TechLog Midrand", "Sealed cargo — high value"),
                ("In Transit", add_days(today(), -2), "N1 — Kroonstad", "Good progress"),
                ("In Transit", add_days(today(), -1), "N1 — Three Sisters", "Overnight rest stop"),
                ("In Transit", today(), "N1 — Beaufort West", "ETA Cape Town: 6 hours"),
            ],
        },
        {
            "label": "Trip 9: AfriMine — Pretoria to Maputo (IN PROGRESS — at border)",
            "order": {"customer": "AfriMine Resources", "order_date": add_days(today(), -1),
                      "pickup_location": "AfriMine Depot — Pretoria West",
                      "delivery_location": "Maputo Port — Cargo Terminal",
                      "cargo_description": "Excavator parts — 22 tons", "weight": 22,
                      "requested_delivery_date": add_days(today(), 0)},
            "trip": {"truck": "TRK-003-KZN", "driver": drivers[2],
                     "route": "Pretoria \u2192 Maputo",
                     "planned_start_date": add_days(today(), -1),
                     "planned_end_date": today(),
                     "revenue": 30800,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3800},
                         {"cost_type": "Permits", "planned_amount": 2500},
                         {"cost_type": "Driver Allowance", "planned_amount": 1000},
                     ]},
            "action": "start",
            "checkpoints": [
                ("Picked Up", add_days(today(), -1), "AfriMine Pretoria", "Heavy load — 22 tons"),
                ("In Transit", add_days(today(), -1), "N4 — Nelspruit", "Approaching border"),
                ("At Border", today(), "Lebombo Border Post", "In customs queue — estimated 3hr wait"),
            ],
        },

        # ── DRAFT TRIPS (booked but not yet started) ──
        {
            "label": "Trip 10: Steelworks — JHB to Durban (DRAFT — tomorrow)",
            "order": {"customer": "Steelworks SA", "order_date": today(),
                      "pickup_location": "Steelworks SA — Germiston Plant",
                      "delivery_location": "Durban Port — Terminal 2",
                      "cargo_description": "Steel plates — 26 tons", "weight": 26,
                      "requested_delivery_date": add_days(today(), 2)},
            "trip": {"truck": "TRK-001-GP", "driver": drivers[0],
                     "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": add_days(today(), 1),
                     "planned_end_date": add_days(today(), 2),
                     "revenue": 15000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 850},
                         {"cost_type": "Driver Allowance", "planned_amount": 600},
                     ]},
            "action": "draft",
            "checkpoints": [],
        },
        {
            "label": "Trip 11: FreshCo — Durban to Cape Town (DRAFT — next week)",
            "order": {"customer": "FreshCo Foods", "order_date": today(),
                      "pickup_location": "FreshCo Cold Store — Durban North",
                      "delivery_location": "FreshCo Cape Town — Philippi",
                      "cargo_description": "Fresh produce — 18 tons (refrigerated)", "weight": 18,
                      "requested_delivery_date": add_days(today(), 5)},
            "trip": {"truck": "TRK-003-KZN", "driver": drivers[2],
                     "route": "Durban \u2192 Cape Town",
                     "planned_start_date": add_days(today(), 3),
                     "planned_end_date": add_days(today(), 5),
                     "revenue": 36300,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 10000},
                         {"cost_type": "Toll Fees", "planned_amount": 1900},
                         {"cost_type": "Driver Allowance", "planned_amount": 1800},
                     ]},
            "action": "draft",
            "checkpoints": [],
        },
    ]

    for s in scenarios:
        order = frappe.get_doc({"doctype": "Transport Order", **s["order"]})
        order.insert(ignore_permissions=True)
        order.submit()

        trip_data = s["trip"].copy()
        trip_data["transport_order"] = order.name

        trip = frappe.get_doc({"doctype": "Trip", **trip_data})
        trip.insert(ignore_permissions=True)

        if s["action"] in ("start", "complete"):
            trip.status = "In Progress"
            trip.actual_start_date = trip.planned_start_date
            # Add checkpoints manually (not via start_trip to control timestamps)
            for cp_type, cp_date, cp_loc, cp_notes in s.get("checkpoints", []):
                trip.append("checkpoints", {
                    "checkpoint_type": cp_type,
                    "timestamp": f"{cp_date} 08:00:00",
                    "location": cp_loc,
                    "notes": cp_notes,
                })
            trip.save(ignore_permissions=True)

        if s["action"] == "complete":
            trip.status = "Completed"
            trip.actual_end_date = trip.planned_end_date
            trip.delivery_confirmation_date = trip.planned_end_date
            trip.save(ignore_permissions=True)

        status_icon = {"Draft": "  ", "In Progress": ">>", "Completed": "OK"}
        print(f"  [{status_icon.get(trip.status, '??')}] {trip.name} | {trip.customer_name} | {trip.status} | Rev: {trip.revenue} | Profit: {trip.gross_profit}")

    frappe.db.commit()
    print(f"  [OK] {len(scenarios)} Orders + Trips created")


def _create_fuel_logs():
    if frappe.db.count("Fuel Log") > 0:
        return

    drivers = [d.name for d in frappe.get_all("Driver", fields=["name"], order_by="creation")]

    logs = [
        # TRK-001 — efficient driver (John)
        {"date": add_days(today(), -21), "truck": "TRK-001-GP", "driver": drivers[0],
         "liters": 220, "cost_per_liter": 18.50, "odometer_reading": 124000, "fuel_station": "Engen — Germiston"},
        {"date": add_days(today(), -20), "truck": "TRK-001-GP", "driver": drivers[0],
         "liters": 180, "cost_per_liter": 18.75, "odometer_reading": 124580, "fuel_station": "Shell — Durban N3"},
        {"date": add_days(today(), -9), "truck": "TRK-001-GP", "driver": drivers[0],
         "liters": 230, "cost_per_liter": 18.60, "odometer_reading": 125200, "fuel_station": "BP — Midrand"},
        {"date": add_days(today(), -8), "truck": "TRK-001-GP", "driver": drivers[0],
         "liters": 190, "cost_per_liter": 18.80, "odometer_reading": 125780, "fuel_station": "Total — Durban"},

        # TRK-002 — long haul (Peter)
        {"date": add_days(today(), -18), "truck": "TRK-002-GP", "driver": drivers[1],
         "liters": 350, "cost_per_liter": 18.50, "odometer_reading": 88000, "fuel_station": "Engen — Midrand"},
        {"date": add_days(today(), -17), "truck": "TRK-002-GP", "driver": drivers[1],
         "liters": 280, "cost_per_liter": 18.90, "odometer_reading": 89200, "fuel_station": "Caltex — Beaufort West"},
        {"date": add_days(today(), -2), "truck": "TRK-002-GP", "driver": drivers[1],
         "liters": 340, "cost_per_liter": 18.65, "odometer_reading": 90600, "fuel_station": "Shell — Johannesburg"},

        # TRK-003 — refrigerated (higher consumption)
        {"date": add_days(today(), -14), "truck": "TRK-003-KZN", "driver": drivers[2],
         "liters": 420, "cost_per_liter": 18.50, "odometer_reading": 66000, "fuel_station": "Total — Durban"},
        {"date": add_days(today(), -12), "truck": "TRK-003-KZN", "driver": drivers[2],
         "liters": 380, "cost_per_liter": 19.10, "odometer_reading": 67400, "fuel_station": "BP — East London"},

        # TRK-004 — less efficient (David, newer driver)
        {"date": add_days(today(), -7), "truck": "TRK-004-WC", "driver": drivers[3],
         "liters": 200, "cost_per_liter": 18.50, "odometer_reading": 45000, "fuel_station": "Engen — Kempton Park"},
        {"date": add_days(today(), -4), "truck": "TRK-004-WC", "driver": drivers[3],
         "liters": 190, "cost_per_liter": 18.75, "odometer_reading": 45400, "fuel_station": "Shell — Bloemfontein"},
    ]

    for l in logs:
        frappe.get_doc({"doctype": "Fuel Log", **l}).insert(ignore_permissions=True)

    print(f"  [OK] {len(logs)} Fuel Logs (4 trucks, realistic consumption patterns)")
