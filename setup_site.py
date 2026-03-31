"""Setup script for ERPNext Transport ERP demo data."""
import frappe


def run():
    frappe.set_user("Administrator")

    # Basic ERPNext fixtures
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

    for uom in ["Nos", "Kg", "Km", "Liter", "Trip"]:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

    frappe.db.commit()

    if not frappe.db.exists("Company", "Transport Co"):
        frappe.get_doc({
            "doctype": "Company", "company_name": "Transport Co", "abbr": "TC",
            "default_currency": "USD", "country": "South Africa", "enable_perpetual_inventory": 0,
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    frappe.defaults.set_global_default("company", "Transport Co")
    frappe.defaults.set_global_default("currency", "USD")
    frappe.defaults.set_global_default("country", "South Africa")
    frappe.db.commit()

    if not frappe.db.exists("Item", "Transport Service"):
        frappe.get_doc({
            "doctype": "Item", "item_code": "Transport Service", "item_name": "Transport Service",
            "item_group": "Services", "is_stock_item": 0, "stock_uom": "Nos",
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    print("Base setup complete. Loading demo data...")
    _load_demo_data()


def _load_demo_data():
    # Trucks
    trucks = [
        {"registration_number": "TRK-001-GP", "truck_type": "Flatbed", "capacity_tons": 30, "make": "Mercedes", "model": "Actros", "year": 2023},
        {"registration_number": "TRK-002-GP", "truck_type": "Container", "capacity_tons": 25, "make": "Volvo", "model": "FH16", "year": 2024},
        {"registration_number": "TRK-003-KZN", "truck_type": "Tanker", "capacity_tons": 20, "make": "Scania", "model": "R500", "year": 2022},
    ]
    for t in trucks:
        if not frappe.db.exists("Truck", t["registration_number"]):
            frappe.get_doc({"doctype": "Truck", "status": "Active", **t}).insert(ignore_permissions=True)
            print(f"  Truck: {t['registration_number']}")

    # Drivers
    drivers = [
        {"driver_name": "John Mokoena", "license_number": "LIC-2024-001", "phone": "+27821234567", "assigned_truck": "TRK-001-GP"},
        {"driver_name": "Peter Nkosi", "license_number": "LIC-2024-002", "phone": "+27829876543", "assigned_truck": "TRK-002-GP"},
        {"driver_name": "Sipho Dlamini", "license_number": "LIC-2024-003", "phone": "+27831112222", "assigned_truck": "TRK-003-KZN"},
    ]
    for d in drivers:
        if not frappe.db.exists("Driver", {"license_number": d["license_number"]}):
            frappe.get_doc({"doctype": "Driver", "status": "Active", **d}).insert(ignore_permissions=True)
            print(f"  Driver: {d['driver_name']}")

    # Routes
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
            print(f"  Route: {rname}")

    # Customers
    for cname in ["ABC Logistics", "XYZ Transport", "Delta Cargo", "Southern Express"]:
        if not frappe.db.exists("Customer", cname):
            frappe.get_doc({
                "doctype": "Customer", "customer_name": cname, "customer_type": "Company",
                "customer_group": "All Customer Groups", "territory": "All Territories"
            }).insert(ignore_permissions=True)

    frappe.db.commit()

    # Only create demo trips if none exist
    if frappe.db.count("Trip") > 0:
        print("Demo trips already exist, skipping...")
        return

    # Transport Orders and Trips
    demo_data = [
        {
            "order": {"customer": "ABC Logistics", "order_date": "2026-03-20", "pickup_location": "Johannesburg Warehouse",
                      "delivery_location": "Durban Port", "cargo_description": "Steel coils - 25 tons", "weight": 25,
                      "requested_delivery_date": "2026-03-22"},
            "trip": {"truck": "TRK-001-GP", "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": "2026-03-20", "planned_end_date": "2026-03-21", "revenue": 15000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 800},
                         {"cost_type": "Permits", "planned_amount": 200},
                         {"cost_type": "Driver Allowance", "planned_amount": 500},
                         {"cost_type": "Mileage", "planned_amount": 1000},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 4200},
                         {"cost_type": "Toll Fees", "actual_amount": 850},
                         {"cost_type": "Permits", "actual_amount": 200},
                         {"cost_type": "Driver Allowance", "actual_amount": 500},
                         {"cost_type": "Mileage", "actual_amount": 1100},
                     ]},
            "complete": True,
        },
        {
            "order": {"customer": "XYZ Transport", "order_date": "2026-03-22", "pickup_location": "Pretoria Factory",
                      "delivery_location": "Cape Town Depot", "cargo_description": "Electronics - 15 tons", "weight": 15,
                      "requested_delivery_date": "2026-03-25"},
            "trip": {"truck": "TRK-002-GP", "route": "Johannesburg \u2192 Cape Town",
                     "planned_start_date": "2026-03-22", "planned_end_date": "2026-03-24", "revenue": 28000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 8000},
                         {"cost_type": "Toll Fees", "planned_amount": 1500},
                         {"cost_type": "Permits", "planned_amount": 300},
                         {"cost_type": "Driver Allowance", "planned_amount": 1200},
                         {"cost_type": "Mileage", "planned_amount": 2500},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 7500},
                         {"cost_type": "Toll Fees", "actual_amount": 1400},
                         {"cost_type": "Permits", "actual_amount": 300},
                         {"cost_type": "Driver Allowance", "actual_amount": 1200},
                         {"cost_type": "Mileage", "actual_amount": 2300},
                     ]},
            "complete": True,
        },
        {
            "order": {"customer": "Delta Cargo", "order_date": "2026-03-25", "pickup_location": "Durban Harbor",
                      "delivery_location": "Cape Town Distribution Center", "cargo_description": "Food products - 20 tons", "weight": 20,
                      "requested_delivery_date": "2026-03-28"},
            "trip": {"truck": "TRK-003-KZN", "route": "Durban \u2192 Cape Town",
                     "planned_start_date": "2026-03-25", "planned_end_date": "2026-03-27", "revenue": 32000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 9000},
                         {"cost_type": "Toll Fees", "planned_amount": 1800},
                         {"cost_type": "Permits", "planned_amount": 400},
                         {"cost_type": "Driver Allowance", "planned_amount": 1500},
                         {"cost_type": "Mileage", "planned_amount": 3000},
                     ],
                     "actual_costs": [
                         {"cost_type": "Diesel/Fuel", "actual_amount": 9500},
                         {"cost_type": "Toll Fees", "actual_amount": 1850},
                         {"cost_type": "Permits", "actual_amount": 400},
                         {"cost_type": "Driver Allowance", "actual_amount": 1500},
                         {"cost_type": "Repairs", "actual_amount": 2500},
                         {"cost_type": "Mileage", "actual_amount": 3200},
                     ]},
            "complete": True,
        },
        {
            "order": {"customer": "Southern Express", "order_date": "2026-03-28", "pickup_location": "Pretoria Industrial",
                      "delivery_location": "Maputo Port", "cargo_description": "Mining equipment - 18 tons", "weight": 18,
                      "requested_delivery_date": "2026-03-30"},
            "trip": {"truck": "TRK-001-GP", "route": "Pretoria \u2192 Maputo",
                     "planned_start_date": "2026-03-28", "planned_end_date": "2026-03-29", "revenue": 22000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3800},
                         {"cost_type": "Toll Fees", "planned_amount": 600},
                         {"cost_type": "Permits", "planned_amount": 1500},
                         {"cost_type": "Driver Allowance", "planned_amount": 800},
                         {"cost_type": "Mileage", "planned_amount": 1200},
                     ]},
            "complete": False,  # This one stays in progress
        },
        {
            "order": {"customer": "ABC Logistics", "order_date": "2026-03-29", "pickup_location": "Johannesburg Airport",
                      "delivery_location": "Durban Warehouse", "cargo_description": "Automotive parts - 22 tons", "weight": 22,
                      "requested_delivery_date": "2026-04-01"},
            "trip": {"truck": "TRK-002-GP", "route": "Johannesburg \u2192 Durban",
                     "planned_start_date": "2026-03-30", "planned_end_date": "2026-03-31", "revenue": 14000,
                     "planned_costs": [
                         {"cost_type": "Diesel/Fuel", "planned_amount": 3500},
                         {"cost_type": "Toll Fees", "planned_amount": 800},
                         {"cost_type": "Driver Allowance", "planned_amount": 500},
                         {"cost_type": "Mileage", "planned_amount": 1000},
                     ]},
            "complete": False,  # Draft - not yet started
            "start": False,
        },
    ]

    driver_list = frappe.get_all("Driver", fields=["name"], limit=3)
    driver_names = [d.name for d in driver_list]

    for i, d in enumerate(demo_data):
        order = frappe.get_doc({"doctype": "Transport Order", **d["order"]})
        order.insert(ignore_permissions=True)
        order.submit()

        trip_data = d["trip"].copy()
        trip_data["transport_order"] = order.name
        trip_data["driver"] = driver_names[i % len(driver_names)]

        trip = frappe.get_doc({"doctype": "Trip", **trip_data})
        trip.insert(ignore_permissions=True)

        if d.get("start", True):
            trip.start_trip()
            trip.reload()

        if d.get("complete", False):
            trip.complete_trip()
            trip.reload()

        status_icon = {"Draft": "📋", "In Progress": "🚛", "Completed": "✅"}
        print(f"  {status_icon.get(trip.status, '')} {trip.name} | {trip.customer_name} | {trip.status} | Profit: {trip.gross_profit}")

    frappe.db.commit()
    print("\nDemo data loaded successfully!")
