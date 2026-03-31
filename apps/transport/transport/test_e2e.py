import frappe

def run():
    frappe.set_user("Administrator")

    # Setup: ensure basic ERPNext setup exists
    # Create Company if needed
    if not frappe.db.exists("Company", "Transport Co"):
        company = frappe.get_doc({
            "doctype": "Company",
            "company_name": "Transport Co",
            "abbr": "TC",
            "default_currency": "USD",
            "country": "South Africa",
            "enable_perpetual_inventory": 0
        })
        company.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Company created: {company.name}")

    # Set default company
    frappe.defaults.set_global_default("company", "Transport Co")

    # Customer Group
    if not frappe.db.exists("Customer Group", "All Customer Groups"):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "All Customer Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Customer Group created")

    # Territory
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Territory created")

    frappe.db.commit()

    # Clean up previous test data
    for dt in ["Trip", "Transport Order"]:
        for d in frappe.get_all(dt, filters={"docstatus": ["!=", 2]}):
            doc = frappe.get_doc(dt, d.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc(dt, d.name, force=True)

    for dt in ["Truck", "Driver", "Route"]:
        for d in frappe.get_all(dt):
            frappe.delete_doc(dt, d.name, force=True)

    frappe.db.commit()

    # === TEST START ===

    # 1. Create Truck
    truck = frappe.get_doc({
        "doctype": "Truck",
        "registration_number": "TRK-001-GP",
        "truck_type": "Flatbed",
        "capacity_tons": 30,
        "status": "Active",
        "make": "Mercedes",
        "model": "Actros",
        "year": 2023
    })
    truck.insert(ignore_permissions=True)
    print(f"1. Truck created: {truck.name}")

    # Create second truck
    truck2 = frappe.get_doc({
        "doctype": "Truck",
        "registration_number": "TRK-002-GP",
        "truck_type": "Container",
        "capacity_tons": 25,
        "status": "Active",
        "make": "Volvo",
        "model": "FH16",
        "year": 2024
    })
    truck2.insert(ignore_permissions=True)
    print(f"   Truck 2 created: {truck2.name}")

    # 2. Create Drivers
    driver = frappe.get_doc({
        "doctype": "Driver",
        "driver_name": "John Mokoena",
        "license_number": "LIC-2024-001",
        "phone": "+27821234567",
        "status": "Active",
        "assigned_truck": truck.name
    })
    driver.insert(ignore_permissions=True)
    print(f"2. Driver created: {driver.name}")

    driver2 = frappe.get_doc({
        "doctype": "Driver",
        "driver_name": "Peter Nkosi",
        "license_number": "LIC-2024-002",
        "phone": "+27829876543",
        "status": "Active",
        "assigned_truck": truck2.name
    })
    driver2.insert(ignore_permissions=True)
    print(f"   Driver 2 created: {driver2.name}")

    # 3. Create Routes
    route1 = frappe.get_doc({
        "doctype": "Route",
        "origin": "Johannesburg",
        "destination": "Durban",
        "estimated_distance_km": 580,
        "estimated_time_hours": 6.5
    })
    route1.insert(ignore_permissions=True)
    print(f"3. Route created: {route1.name}")

    route2 = frappe.get_doc({
        "doctype": "Route",
        "origin": "Johannesburg",
        "destination": "Cape Town",
        "estimated_distance_km": 1400,
        "estimated_time_hours": 14
    })
    route2.insert(ignore_permissions=True)
    print(f"   Route 2 created: {route2.name}")

    # 4. Create Customers
    for cname in ["ABC Logistics", "XYZ Transport", "Delta Cargo"]:
        if not frappe.db.exists("Customer", cname):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cname,
                "customer_type": "Company",
                "customer_group": "All Customer Groups",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)
    print("4. Customers created")

    # 5. Create Transport Orders
    order1 = frappe.get_doc({
        "doctype": "Transport Order",
        "customer": "ABC Logistics",
        "order_date": "2026-03-25",
        "pickup_location": "Johannesburg Warehouse",
        "delivery_location": "Durban Port",
        "cargo_description": "Steel coils - 25 tons",
        "weight": 25,
        "requested_delivery_date": "2026-03-27"
    })
    order1.insert(ignore_permissions=True)
    order1.submit()
    print(f"5. Order 1: {order1.name} -> {order1.status}")

    order2 = frappe.get_doc({
        "doctype": "Transport Order",
        "customer": "XYZ Transport",
        "order_date": "2026-03-26",
        "pickup_location": "Pretoria Factory",
        "delivery_location": "Cape Town Depot",
        "cargo_description": "Electronics - 15 tons",
        "weight": 15,
        "requested_delivery_date": "2026-03-29"
    })
    order2.insert(ignore_permissions=True)
    order2.submit()
    print(f"   Order 2: {order2.name} -> {order2.status}")

    order3 = frappe.get_doc({
        "doctype": "Transport Order",
        "customer": "Delta Cargo",
        "order_date": "2026-03-28",
        "pickup_location": "Johannesburg CBD",
        "delivery_location": "Durban North",
        "cargo_description": "Food products - 20 tons",
        "weight": 20,
        "requested_delivery_date": "2026-03-30"
    })
    order3.insert(ignore_permissions=True)
    order3.submit()
    print(f"   Order 3: {order3.name} -> {order3.status}")

    frappe.db.commit()

    # 6. Create Trips
    # Trip 1 - Completed, profitable
    trip1 = frappe.get_doc({
        "doctype": "Trip",
        "transport_order": order1.name,
        "truck": truck.name,
        "driver": driver.name,
        "route": route1.name,
        "planned_start_date": "2026-03-25",
        "planned_end_date": "2026-03-26",
        "revenue": 15000,
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
        ]
    })
    trip1.insert(ignore_permissions=True)

    print(f"\n6. Trip 1: {trip1.name}")
    print(f"   Planned: {trip1.total_planned_cost} | Actual: {trip1.total_actual_cost}")
    print(f"   Variance: {trip1.total_variance} ({trip1.variance_percentage:.1f}%)")
    print(f"   Budget: {trip1.budget_status}")
    print(f"   Revenue: {trip1.revenue} | Profit: {trip1.gross_profit} ({trip1.profit_margin:.1f}%)")

    # Start and complete trip 1
    trip1.start_trip()
    trip1.reload()
    print(f"   -> Started: {trip1.status} (Date: {trip1.actual_start_date})")
    trip1.complete_trip()
    trip1.reload()
    print(f"   -> Completed: {trip1.status} (Delivered: {trip1.delivery_confirmation_date})")

    # Trip 2 - Cape Town, under budget
    trip2 = frappe.get_doc({
        "doctype": "Trip",
        "transport_order": order2.name,
        "truck": truck2.name,
        "driver": driver2.name,
        "route": route2.name,
        "planned_start_date": "2026-03-26",
        "planned_end_date": "2026-03-28",
        "revenue": 28000,
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
        ]
    })
    trip2.insert(ignore_permissions=True)
    trip2.start_trip()
    trip2.reload()
    trip2.complete_trip()
    trip2.reload()

    print(f"\n   Trip 2: {trip2.name}")
    print(f"   Planned: {trip2.total_planned_cost} | Actual: {trip2.total_actual_cost}")
    print(f"   Variance: {trip2.total_variance} ({trip2.variance_percentage:.1f}%)")
    print(f"   Budget: {trip2.budget_status}")
    print(f"   Profit: {trip2.gross_profit} ({trip2.profit_margin:.1f}%)")

    # Trip 3 - In Progress
    trip3 = frappe.get_doc({
        "doctype": "Trip",
        "transport_order": order3.name,
        "truck": truck.name,
        "driver": driver.name,
        "route": route1.name,
        "planned_start_date": "2026-03-28",
        "planned_end_date": "2026-03-29",
        "revenue": 12000,
        "planned_costs": [
            {"cost_type": "Diesel/Fuel", "planned_amount": 3200},
            {"cost_type": "Toll Fees", "planned_amount": 800},
            {"cost_type": "Driver Allowance", "planned_amount": 500},
        ],
    })
    trip3.insert(ignore_permissions=True)
    trip3.start_trip()
    trip3.reload()

    print(f"\n   Trip 3: {trip3.name} (Status: {trip3.status}) - In Progress, no actual costs yet")

    frappe.db.commit()

    # === VERIFICATION ===
    total_trips = frappe.db.count("Trip")
    total_orders = frappe.db.count("Transport Order")
    total_trucks = frappe.db.count("Truck")
    total_drivers = frappe.db.count("Driver")
    total_routes = frappe.db.count("Route")

    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"  Trucks: {total_trucks}")
    print(f"  Drivers: {total_drivers}")
    print(f"  Routes: {total_routes}")
    print(f"  Transport Orders: {total_orders}")
    print(f"  Trips: {total_trips}")
    print(f"{'='*50}")
    print(f"\n=== END-TO-END TEST PASSED ===")
