"""
Optional demo data loader for Transport module.

Usage:
    bench --site erp.localhost execute transport.demo.load
"""
import frappe
from frappe.utils import add_days, today


def load():
    """Load demo data for Transport module. Safe to run multiple times."""
    frappe.set_user("Administrator")

    print("Loading Transport demo data...")

    _ensure_fixtures()
    _create_trucks()
    _create_drivers()
    _create_routes()
    _create_customers()
    _create_rate_cards()
    _create_orders_and_trips()
    _create_fuel_logs()

    frappe.db.commit()
    print("\nDemo data loaded successfully!")
    print("  Visit: /app/transport")


def _ensure_fixtures():
    """Create basic ERPNext fixtures if missing."""
    for wt in ["Transit", "Store"]:
        if not frappe.db.exists("Warehouse Type", wt):
            frappe.get_doc({"doctype": "Warehouse Type", "name": wt}).insert(ignore_permissions=True)

    for name, is_group, parent in [
        ("All Customer Groups", 1, None),
        ("All Territories", 1, None),
        ("All Supplier Groups", 1, None),
        ("All Item Groups", 1, None),
        ("Services", 0, "All Item Groups"),
    ]:
        dt = "Customer Group" if "Customer" in name else "Territory" if "Territor" in name else "Supplier Group" if "Supplier" in name else "Item Group"
        name_field = dt.lower().replace(" ", "_") + "_name"
        if not frappe.db.exists(dt, name):
            doc = {"doctype": dt, name_field: name, "is_group": is_group}
            if parent:
                doc[f"parent_{dt.lower().replace(' ', '_')}"] = parent
            frappe.get_doc(doc).insert(ignore_permissions=True)

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
    print("  Fixtures ready")


def _create_trucks():
    trucks = [
        {"registration_number": "TRK-001-GP", "truck_type": "Flatbed", "capacity_tons": 30, "make": "Mercedes", "model": "Actros", "year": 2023},
        {"registration_number": "TRK-002-GP", "truck_type": "Container", "capacity_tons": 25, "make": "Volvo", "model": "FH16", "year": 2024},
        {"registration_number": "TRK-003-KZN", "truck_type": "Tanker", "capacity_tons": 20, "make": "Scania", "model": "R500", "year": 2022},
    ]
    for t in trucks:
        if not frappe.db.exists("Truck", t["registration_number"]):
            frappe.get_doc({"doctype": "Truck", "status": "Active", **t}).insert(ignore_permissions=True)
    print("  3 Trucks created")


def _create_drivers():
    drivers = [
        {"driver_name": "John Mokoena", "license_number": "LIC-2024-001", "phone": "+27821234567", "assigned_truck": "TRK-001-GP"},
        {"driver_name": "Peter Nkosi", "license_number": "LIC-2024-002", "phone": "+27829876543", "assigned_truck": "TRK-002-GP"},
        {"driver_name": "Sipho Dlamini", "license_number": "LIC-2024-003", "phone": "+27831112222", "assigned_truck": "TRK-003-KZN"},
    ]
    for d in drivers:
        if not frappe.db.exists("Driver", {"license_number": d["license_number"]}):
            frappe.get_doc({"doctype": "Driver", "status": "Active", **d}).insert(ignore_permissions=True)
    print("  3 Drivers created")


def _create_routes():
    routes = [
        {"origin": "Johannesburg", "destination": "Durban", "estimated_distance_km": 580, "estimated_time_hours": 6.5},
        {"origin": "Johannesburg", "destination": "Cape Town", "estimated_distance_km": 1400, "estimated_time_hours": 14},
        {"origin": "Durban", "destination": "Cape Town", "estimated_distance_km": 1650, "estimated_time_hours": 17},
        {"origin": "Pretoria", "destination": "Maputo", "estimated_distance_km": 560, "estimated_time_hours": 7},
    ]
    for r in routes:
        rname = f"{r['origin']} \u2192 {r['destination']}"
        if not frappe.db.exists("Route", rname):
            frappe.get_doc({"doctype": "Route", **r}).insert(ignore_permissions=True)
    print("  4 Routes created")


def _create_customers():
    for cname in ["ABC Logistics", "XYZ Transport", "Delta Cargo", "Southern Express"]:
        if not frappe.db.exists("Customer", cname):
            frappe.get_doc({
                "doctype": "Customer", "customer_name": cname, "customer_type": "Company",
                "customer_group": "All Customer Groups", "territory": "All Territories",
            }).insert(ignore_permissions=True)
    print("  4 Customers created")


def _create_rate_cards():
    if frappe.db.count("Transport Rate Card") > 0:
        return

    cards = [
        {"customer": "ABC Logistics", "route": "Johannesburg \u2192 Durban", "rate_type": "Fixed per Trip", "rate_per_trip": 15000,
         "effective_from": add_days(today(), -90), "effective_to": add_days(today(), 90)},
        {"customer": "XYZ Transport", "route": "Johannesburg \u2192 Cape Town", "rate_type": "Fixed per Trip", "rate_per_trip": 28000,
         "effective_from": add_days(today(), -60), "effective_to": add_days(today(), 120)},
        {"customer": "Delta Cargo", "route": "Durban \u2192 Cape Town", "rate_type": "Per Km", "rate_per_km": 19.5,
         "effective_from": add_days(today(), -30), "effective_to": add_days(today(), 150)},
        {"customer": "Southern Express", "route": "Pretoria \u2192 Maputo", "rate_type": "Per Ton", "rate_per_ton": 1200,
         "effective_from": add_days(today(), -45), "effective_to": add_days(today(), 45)},
    ]
    for c in cards:
        frappe.get_doc({"doctype": "Transport Rate Card", "status": "Active", **c}).insert(ignore_permissions=True)
    print("  4 Rate Cards created")


def _create_orders_and_trips():
    if frappe.db.count("Trip") > 0:
        print("  Trips already exist, skipping...")
        return

    driver_list = frappe.get_all("Driver", fields=["name"], limit=3)
    drivers = [d.name for d in driver_list]

    demo = [
        {
            "order": {"customer": "ABC Logistics", "order_date": add_days(today(), -10),
                      "pickup_location": "Johannesburg Warehouse", "delivery_location": "Durban Port",
                      "cargo_description": "Steel coils - 25 tons", "weight": 25,
                      "requested_delivery_date": add_days(today(), -8)},
            "trip": {"truck": "TRK-001-GP", "driver": drivers[0], "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": add_days(today(), -10), "planned_end_date": add_days(today(), -9),
                     "revenue": 15000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 800},
                         {"cost_type": "Driver Allowance", "planned_amount": 500},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 4200},
                         {"cost_type": "Toll Fees", "actual_amount": 850},
                         {"cost_type": "Driver Allowance", "actual_amount": 500},
                     ]},
            "complete": True,
        },
        {
            "order": {"customer": "XYZ Transport", "order_date": add_days(today(), -7),
                      "pickup_location": "Pretoria Factory", "delivery_location": "Cape Town Depot",
                      "cargo_description": "Electronics - 15 tons", "weight": 15,
                      "requested_delivery_date": add_days(today(), -4)},
            "trip": {"truck": "TRK-002-GP", "driver": drivers[1], "route": "Johannesburg \u2192 Cape Town",
                     "planned_start_date": add_days(today(), -7), "planned_end_date": add_days(today(), -5),
                     "revenue": 28000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 8000},
                         {"cost_type": "Toll Fees", "planned_amount": 1500},
                         {"cost_type": "Driver Allowance", "planned_amount": 1200},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 7500},
                         {"cost_type": "Toll Fees", "actual_amount": 1400},
                         {"cost_type": "Driver Allowance", "actual_amount": 1200},
                     ]},
            "complete": True,
        },
        {
            "order": {"customer": "Delta Cargo", "order_date": add_days(today(), -3),
                      "pickup_location": "Durban Harbor", "delivery_location": "Cape Town DC",
                      "cargo_description": "Food products - 20 tons", "weight": 20,
                      "requested_delivery_date": add_days(today(), 1)},
            "trip": {"truck": "TRK-003-KZN", "driver": drivers[2], "route": "Durban \u2192 Cape Town",
                     "planned_start_date": add_days(today(), -3), "planned_end_date": add_days(today(), -1),
                     "revenue": 32000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 9000},
                         {"cost_type": "Toll Fees", "planned_amount": 1800},
                         {"cost_type": "Driver Allowance", "planned_amount": 1500},
                     ]},
            "complete": False,
        },
    ]

    for d in demo:
        order = frappe.get_doc({"doctype": "Transport Order", **d["order"]})
        order.insert(ignore_permissions=True)
        order.submit()

        trip = frappe.get_doc({"doctype": "Trip", "transport_order": order.name, **d["trip"]})
        trip.insert(ignore_permissions=True)
        trip.start_trip()
        trip.reload()

        if d["complete"]:
            trip.complete_trip()
            trip.reload()

        print(f"  {trip.name} | {trip.customer_name} | {trip.status}")

    print("  3 Orders + 3 Trips created")


def _create_fuel_logs():
    if frappe.db.count("Fuel Log") > 0:
        return

    logs = [
        {"date": add_days(today(), -10), "truck": "TRK-001-GP", "liters": 250, "cost_per_liter": 18.50,
         "odometer_reading": 125000, "fuel_station": "Engen Midrand"},
        {"date": add_days(today(), -9), "truck": "TRK-001-GP", "liters": 180, "cost_per_liter": 18.75,
         "odometer_reading": 125580, "fuel_station": "Shell Durban"},
        {"date": add_days(today(), -7), "truck": "TRK-002-GP", "liters": 350, "cost_per_liter": 18.50,
         "odometer_reading": 89000, "fuel_station": "BP Johannesburg"},
        {"date": add_days(today(), -5), "truck": "TRK-002-GP", "liters": 320, "cost_per_liter": 19.00,
         "odometer_reading": 90400, "fuel_station": "Caltex Cape Town"},
        {"date": add_days(today(), -3), "truck": "TRK-003-KZN", "liters": 400, "cost_per_liter": 18.60,
         "odometer_reading": 67000, "fuel_station": "Total Durban"},
    ]

    driver_list = frappe.get_all("Driver", fields=["name"], limit=3)
    drivers = [d.name for d in driver_list]

    for i, l in enumerate(logs):
        l["driver"] = drivers[i % len(drivers)]
        frappe.get_doc({"doctype": "Fuel Log", **l}).insert(ignore_permissions=True)

    print("  5 Fuel Logs created")
