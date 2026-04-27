"""
Transport Module - Demo Data Loader (Zambia edition)

Creates a realistic dataset set in Zambia with ZMW as base currency and USD
as secondary transaction currency (for cross-border trips).

- 5 trucks (3 profitable, 1 average, 1 in maintenance)
- 4 drivers (one with soon-to-expire license)
- 5 routes (4 domestic, 1 cross-border to DRC)
- 5 customers (mining, retail, agriculture, manufacturing, retail chain)
- 5 rate cards (one expiring in 10 days)
- 11 trips across Planned / In Progress / Completed states
- Fuel logs with realistic consumption patterns
- 8 seeded Expense Categories mapped to the company's default expense account

Usage:
    bench --site erp.localhost execute transport.demo.load

To reset and reload:
    bench --site erp.localhost execute transport.demo.clear
    bench --site erp.localhost execute transport.demo.load
"""
import frappe
from frappe.utils import add_days, today


COMPANY_NAME = "Zambezi Freight"
COMPANY_ABBR = "ZF"
BASE_CURRENCY = "ZMW"
SECONDARY_CURRENCY = "USD"
COUNTRY = "Zambia"

# Rough ZMW per USD - demo only. Finance can maintain the live rate in
# Currency Exchange records after go-live.
USD_TO_ZMW_RATE = 26.0

EXPENSE_CATEGORIES = [
	("Diesel/Fuel", "Variable"),
	("Toll Fees", "Variable"),
	("Permits", "Variable"),
	("Driver Allowance", "Driver-Related"),
	("Loading & Offloading", "Variable"),
	("Repairs", "Variable"),
	("Border Fees", "Variable"),
	("Other", "Variable"),
]


def load():
	"""Load complete demo data. Safe to run multiple times."""
	frappe.set_user("Administrator")

	print("\n========================================")
	print("  Loading Transport Demo Data (Zambia)...")
	print("========================================\n")

	_ensure_fixtures()
	_ensure_currencies()
	_ensure_company()
	_ensure_expense_categories()
	_ensure_transport_settings()
	_create_trucks()
	_create_drivers()
	_create_routes()
	_create_customers()
	_create_rate_cards()
	_create_orders_and_trips()
	_create_fuel_logs()

	frappe.db.commit()

	print("\n========================================")
	print("  DEMO DATA LOADED")
	print("========================================")
	print(f"  Company:          {COMPANY_NAME}")
	print(f"  Base Currency:    {BASE_CURRENCY}")
	print(f"  Trucks:           {frappe.db.count('Truck')}")
	print(f"  Drivers:          {frappe.db.count('Driver')}")
	print(f"  Routes:           {frappe.db.count('Route')}")
	print(f"  Customers:        {frappe.db.count('Customer')}")
	print(f"  Rate Cards:       {frappe.db.count('Transport Rate Card')}")
	print(f"  Transport Orders: {frappe.db.count('Transport Order')}")
	print(f"  Trips:            {frappe.db.count('Trip')}")
	print(f"  Fuel Logs:        {frappe.db.count('Fuel Log')}")
	print(f"  Expense Cats:     {frappe.db.count('Expense Category')}")
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

	for uom in ["Nos", "Kg", "Km", "Liter", "Ton"]:
		if not frappe.db.exists("UOM", uom):
			frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

	frappe.db.commit()
	print("  [OK] Base fixtures")


def _ensure_currencies():
	for code in (BASE_CURRENCY, SECONDARY_CURRENCY):
		if not frappe.db.exists("Currency", code):
			frappe.get_doc({
				"doctype": "Currency",
				"currency_name": code,
				"enabled": 1,
			}).insert(ignore_permissions=True)

	# USD -> ZMW exchange rate dated today
	if not frappe.db.exists("Currency Exchange", {
		"from_currency": SECONDARY_CURRENCY,
		"to_currency": BASE_CURRENCY,
		"date": today(),
	}):
		frappe.get_doc({
			"doctype": "Currency Exchange",
			"from_currency": SECONDARY_CURRENCY,
			"to_currency": BASE_CURRENCY,
			"date": today(),
			"exchange_rate": USD_TO_ZMW_RATE,
			"for_buying": 1,
			"for_selling": 1,
		}).insert(ignore_permissions=True)

	frappe.db.commit()
	print(f"  [OK] Currencies: {BASE_CURRENCY} (base), {SECONDARY_CURRENCY} @ {USD_TO_ZMW_RATE}")


def _ensure_company():
	# Remove the legacy demo company if present so reports and defaults settle on
	# the Zambia-based company.
	legacy = "Transport Co"
	if frappe.db.exists("Company", legacy) and not frappe.db.exists("Company", COMPANY_NAME):
		# keep legacy but make sure it is not the default
		pass

	if not frappe.db.exists("Company", COMPANY_NAME):
		frappe.get_doc({
			"doctype": "Company",
			"company_name": COMPANY_NAME,
			"abbr": COMPANY_ABBR,
			"default_currency": BASE_CURRENCY,
			"country": COUNTRY,
			"enable_perpetual_inventory": 0,
		}).insert(ignore_permissions=True)
		frappe.db.commit()

	frappe.defaults.set_global_default("company", COMPANY_NAME)
	frappe.defaults.set_global_default("currency", BASE_CURRENCY)
	frappe.defaults.set_global_default("country", COUNTRY)

	# Create a Transport Service item in base currency if missing
	if not frappe.db.exists("Item", "Transport Service"):
		frappe.get_doc({
			"doctype": "Item",
			"item_code": "Transport Service",
			"item_name": "Transport Service",
			"item_group": "Services",
			"is_stock_item": 0,
			"stock_uom": "Nos",
		}).insert(ignore_permissions=True)

	frappe.db.commit()
	print(f"  [OK] Company: {COMPANY_NAME} ({COUNTRY}, base {BASE_CURRENCY})")


def _ensure_expense_categories():
	default_expense_account = frappe.db.get_value(
		"Company", COMPANY_NAME, "default_expense_account"
	)

	for name, ctype in EXPENSE_CATEGORIES:
		if frappe.db.exists("Expense Category", name):
			continue
		doc = frappe.get_doc({
			"doctype": "Expense Category",
			"category_name": name,
			"category_type": ctype,
			"is_active": 1,
		})
		if default_expense_account:
			doc.append("mappings", {
				"company": COMPANY_NAME,
				"expense_account": default_expense_account,
			})
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print(f"  [OK] {len(EXPENSE_CATEGORIES)} Expense Categories seeded")


def _ensure_transport_settings():
	settings = frappe.get_single("Transport Settings")
	if not settings.default_company:
		settings.default_company = COMPANY_NAME
	if not settings.base_currency:
		settings.base_currency = BASE_CURRENCY
	settings.save(ignore_permissions=True)
	frappe.db.commit()
	print("  [OK] Transport Settings defaulted to Zambezi Freight")


# ----------------------------------------------------------------
# MASTER DATA
# ----------------------------------------------------------------


def _create_trucks():
	trucks = [
		{"registration_number": "ABC 1234", "truck_type": "Flatbed", "capacity_tons": 30,
		 "make": "Mercedes", "model": "Actros 2645", "year": 2023, "status": "Active",
		 "notes": "Workhorse for Copperbelt runs"},
		{"registration_number": "BCD 2345", "truck_type": "Container", "capacity_tons": 28,
		 "make": "Volvo", "model": "FH16 540", "year": 2024, "status": "Active",
		 "notes": "Long-haul Lusaka - Livingstone route"},
		{"registration_number": "CDE 3456", "truck_type": "Refrigerated", "capacity_tons": 22,
		 "make": "Scania", "model": "R500", "year": 2022, "status": "Active",
		 "notes": "Agricultural produce - temperature controlled"},
		{"registration_number": "DEF 4567", "truck_type": "Tanker", "capacity_tons": 25,
		 "make": "MAN", "model": "TGX 26.540", "year": 2021, "status": "Active",
		 "notes": "Liquid cargo"},
		{"registration_number": "EFG 5678", "truck_type": "Flatbed", "capacity_tons": 34,
		 "make": "Mercedes", "model": "Actros 2652", "year": 2020, "status": "Maintenance",
		 "notes": "Engine overhaul - expected back in service next week"},
	]
	for t in trucks:
		if not frappe.db.exists("Truck", t["registration_number"]):
			frappe.get_doc({"doctype": "Truck", **t}).insert(ignore_permissions=True)
	print("  [OK] 5 Trucks (4 active, 1 in maintenance)")


def _create_drivers():
	drivers = [
		{"driver_name": "Mwansa Banda", "license_number": "ZM-LIC-2024-001", "phone": "+260977111222",
		 "license_expiry": add_days(today(), 365),
		 "assigned_truck": "ABC 1234", "notes": "Senior driver - 14 years on Copperbelt route"},
		{"driver_name": "Chileshe Mwale", "license_number": "ZM-LIC-2024-002", "phone": "+260966333444",
		 "license_expiry": add_days(today(), 180),
		 "assigned_truck": "BCD 2345", "notes": "Long-haul specialist"},
		{"driver_name": "Kabwe Phiri", "license_number": "ZM-LIC-2024-003", "phone": "+260955555666",
		 "license_expiry": add_days(today(), 20),
		 "assigned_truck": "CDE 3456", "notes": "License renewal due soon"},
		{"driver_name": "Mulenga Tembo", "license_number": "ZM-LIC-2024-004", "phone": "+260977888999",
		 "license_expiry": add_days(today(), 720),
		 "assigned_truck": "DEF 4567", "notes": "Cross-border certified - DRC"},
	]
	for d in drivers:
		if not frappe.db.exists("Driver", {"license_number": d["license_number"]}):
			frappe.get_doc({"doctype": "Driver", "status": "Active", "employment_type": "Employee", **d}).insert(ignore_permissions=True)
	print("  [OK] 4 Drivers (1 with license expiring in 20 days)")


def _create_routes():
	routes = [
		{"origin": "Lusaka", "destination": "Ndola", "estimated_distance_km": 320, "estimated_time_hours": 4.5},
		{"origin": "Lusaka", "destination": "Kitwe", "estimated_distance_km": 360, "estimated_time_hours": 5.0},
		{"origin": "Lusaka", "destination": "Livingstone", "estimated_distance_km": 480, "estimated_time_hours": 6.5},
		{"origin": "Ndola", "destination": "Kasumbalesa", "estimated_distance_km": 100, "estimated_time_hours": 2.0,
		 "notes": "DRC border crossing - USD invoicing, permits required"},
		{"origin": "Lusaka", "destination": "Chipata", "estimated_distance_km": 570, "estimated_time_hours": 7.5},
	]
	for r in routes:
		rname = f"{r['origin']} → {r['destination']}"
		if not frappe.db.exists("Route", rname):
			frappe.get_doc({"doctype": "Route", **r}).insert(ignore_permissions=True)
	print("  [OK] 5 Routes (4 domestic, 1 cross-border to DRC)")


def _create_customers():
	customers = [
		("Copperbelt Mining Ltd", "Mining - heavy cargo, Copperbelt routes"),
		("Zambian Breweries", "Beverages - regular deliveries"),
		("Agro Fresh Zambia", "Perishable produce - refrigerated required"),
		("Kasumbalesa Traders", "Cross-border - DRC, invoiced in USD"),
		("Shoprite Zambia", "Retail distribution - nationwide"),
	]
	for cname, _notes in customers:
		if not frappe.db.exists("Customer", cname):
			frappe.get_doc({
				"doctype": "Customer", "customer_name": cname, "customer_type": "Company",
				"customer_group": "All Customer Groups", "territory": "All Territories",
			}).insert(ignore_permissions=True)
	print("  [OK] 5 Customers (mining, beverages, agri, cross-border, retail)")


def _create_rate_cards():
	if frappe.db.count("Transport Rate Card") > 0:
		return

	cards = [
		# High-volume Copperbelt mining
		{"customer": "Copperbelt Mining Ltd", "route": "Lusaka → Ndola",
		 "rate_type": "Fixed per Trip", "rate_per_trip": 14000,
		 "effective_from": add_days(today(), -180), "effective_to": add_days(today(), 180)},
		# Beverages, per-km
		{"customer": "Zambian Breweries", "route": "Lusaka → Livingstone",
		 "rate_type": "Per Km", "rate_per_km": 52,
		 "effective_from": add_days(today(), -90), "effective_to": add_days(today(), 90)},
		# Agri, per-ton
		{"customer": "Agro Fresh Zambia", "route": "Lusaka → Chipata",
		 "rate_type": "Per Ton", "rate_per_ton": 1200,
		 "effective_from": add_days(today(), -60), "effective_to": add_days(today(), 120)},
		# Cross-border (will be used in USD during trip creation)
		{"customer": "Kasumbalesa Traders", "route": "Ndola → Kasumbalesa",
		 "rate_type": "Fixed per Trip", "rate_per_trip": 45000,
		 "effective_from": add_days(today(), -45), "effective_to": add_days(today(), 135),
		 "notes": "ZMW rate. Cross-border trips may invoice customer in USD."},
		# Expiring soon
		{"customer": "Shoprite Zambia", "route": "Lusaka → Kitwe",
		 "rate_type": "Fixed per Trip", "rate_per_trip": 11500,
		 "effective_from": add_days(today(), -150), "effective_to": add_days(today(), 10),
		 "notes": "Contract up for renewal - client requesting 4% discount"},
	]
	for c in cards:
		frappe.get_doc({"doctype": "Transport Rate Card", "status": "Active", **c}).insert(ignore_permissions=True)
	print("  [OK] 5 Rate Cards (1 expiring in 10 days)")


# ----------------------------------------------------------------
# OPERATIONAL DATA
# ----------------------------------------------------------------


def _create_orders_and_trips():
	if frappe.db.count("Trip") > 0:
		print("  [--] Trips exist, skipping...")
		return

	drivers = [d.name for d in frappe.get_all("Driver", fields=["name"], order_by="creation")]

	scenarios = [
		{
			"label": "Trip 1: Copperbelt Mining - Lusaka to Ndola (profitable, on time)",
			"order": {"customer": "Copperbelt Mining Ltd", "order_date": add_days(today(), -21),
					  "pickup_location": "Copperbelt Mining - Lusaka Yard",
					  "delivery_location": "Ndola Mine Site",
					  "cargo_description": "Mining equipment - 27 tons", "weight": 27,
					  "requested_delivery_date": add_days(today(), -19)},
			"trip": {"truck": "ABC 1234", "driver": drivers[0],
					 "route": "Lusaka → Ndola",
					 "planned_start_date": add_days(today(), -21),
					 "planned_end_date": add_days(today(), -20),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 5300,
					 "revenue": 14000,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 3200},
						 {"cost_type": "Toll Fees", "planned_amount": 800},
						 {"cost_type": "Driver Allowance", "planned_amount": 1000},
						 {"cost_type": "Permits", "planned_amount": 300},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 3100},
						 {"cost_type": "Toll Fees", "actual_amount": 800},
						 {"cost_type": "Driver Allowance", "actual_amount": 1000},
						 {"cost_type": "Permits", "actual_amount": 300},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -21), "Lusaka Yard", "Loaded 27 tons"),
				("In Transit", add_days(today(), -21), "Great North Road - Kapiri Mposhi", "Clear roads"),
				("Delivered", add_days(today(), -20), "Ndola Mine Site", "Offloaded - POD signed"),
			],
		},
		{
			"label": "Trip 2: Zambian Breweries - Lusaka to Livingstone (long haul, profitable)",
			"order": {"customer": "Zambian Breweries", "order_date": add_days(today(), -18),
					  "pickup_location": "ZB Brewery - Lusaka",
					  "delivery_location": "Livingstone Distribution Centre",
					  "cargo_description": "Packaged beverages - 20 tons", "weight": 20,
					  "requested_delivery_date": add_days(today(), -15)},
			"trip": {"truck": "BCD 2345", "driver": drivers[1],
					 "route": "Lusaka → Livingstone",
					 "planned_start_date": add_days(today(), -18),
					 "planned_end_date": add_days(today(), -16),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 15000,
					 "revenue": 52 * 480,  # per-km rate x distance
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 9500},
						 {"cost_type": "Toll Fees", "planned_amount": 1400},
						 {"cost_type": "Driver Allowance", "planned_amount": 1800},
						 {"cost_type": "Permits", "planned_amount": 300},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 9100},
						 {"cost_type": "Toll Fees", "actual_amount": 1400},
						 {"cost_type": "Driver Allowance", "actual_amount": 1800},
						 {"cost_type": "Permits", "actual_amount": 300},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -18), "ZB Lusaka Brewery", "Palletised cargo"),
				("In Transit", add_days(today(), -18), "Kafue Road", "Good progress"),
				("In Transit", add_days(today(), -17), "Mazabuka", "Overnight stop"),
				("Delivered", add_days(today(), -16), "Livingstone DC", "Delivered on schedule"),
			],
		},
		{
			"label": "Trip 3: Agro Fresh - Lusaka to Chipata (OVER BUDGET - breakdown)",
			"order": {"customer": "Agro Fresh Zambia", "order_date": add_days(today(), -14),
					  "pickup_location": "Agro Fresh Cold Store - Lusaka",
					  "delivery_location": "Chipata Distribution Centre",
					  "cargo_description": "Fresh produce - 18 tons (refrigerated)", "weight": 18,
					  "requested_delivery_date": add_days(today(), -11)},
			"trip": {"truck": "CDE 3456", "driver": drivers[2],
					 "route": "Lusaka → Chipata",
					 "planned_start_date": add_days(today(), -14),
					 "planned_end_date": add_days(today(), -12),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 13000,
					 "revenue": 1200 * 18,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 9800},
						 {"cost_type": "Toll Fees", "planned_amount": 1500},
						 {"cost_type": "Driver Allowance", "planned_amount": 1500},
						 {"cost_type": "Permits", "planned_amount": 200},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 10400},
						 {"cost_type": "Toll Fees", "actual_amount": 1500},
						 {"cost_type": "Driver Allowance", "actual_amount": 1500},
						 {"cost_type": "Repairs", "actual_amount": 4200},
						 {"cost_type": "Permits", "actual_amount": 200},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -14), "Agro Fresh Lusaka", "Reefer at 2C"),
				("In Transit", add_days(today(), -14), "Great East Road - Luangwa", "Normal"),
				("Delayed", add_days(today(), -13), "Nyimba", "Cooling unit fault - roadside repair"),
				("In Transit", add_days(today(), -13), "Katete", "Back on road, 4hr delay"),
				("Delivered", add_days(today(), -11), "Chipata DC", "Delivered - client notified of delay"),
			],
		},
		{
			"label": "Trip 4: Kasumbalesa Traders - Ndola to DRC border (cross-border, USD)",
			"order": {"customer": "Kasumbalesa Traders", "order_date": add_days(today(), -12),
					  "pickup_location": "Ndola Warehouse",
					  "delivery_location": "Kasumbalesa Border - DRC side",
					  "cargo_description": "Construction materials - 22 tons", "weight": 22,
					  "requested_delivery_date": add_days(today(), -10)},
			"trip": {"truck": "ABC 1234", "driver": drivers[3],
					 "route": "Ndola → Kasumbalesa",
					 "planned_start_date": add_days(today(), -12),
					 "planned_end_date": add_days(today(), -11),
					 "transaction_currency": SECONDARY_CURRENCY,
					 "exchange_rate": USD_TO_ZMW_RATE,
					 "budget_amount": 1200,  # USD
					 "revenue": 1800,  # USD
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 350},
						 {"cost_type": "Border Fees", "planned_amount": 400},
						 {"cost_type": "Permits", "planned_amount": 200},
						 {"cost_type": "Driver Allowance", "planned_amount": 250},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 360},
						 {"cost_type": "Border Fees", "actual_amount": 400},
						 {"cost_type": "Permits", "actual_amount": 200},
						 {"cost_type": "Driver Allowance", "actual_amount": 250},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -12), "Ndola Warehouse", "Loaded construction cargo"),
				("At Border", add_days(today(), -12), "Kasumbalesa Border Post", "Customs clearance 2hr"),
				("Delivered", add_days(today(), -11), "DRC side - Kasumbalesa", "Delivered on time"),
			],
		},
		{
			"label": "Trip 5: Copperbelt Mining - Lusaka to Ndola #2",
			"order": {"customer": "Copperbelt Mining Ltd", "order_date": add_days(today(), -9),
					  "pickup_location": "Copperbelt Mining - Lusaka Yard",
					  "delivery_location": "Ndola Mine Site",
					  "cargo_description": "Spare parts - 24 tons", "weight": 24,
					  "requested_delivery_date": add_days(today(), -7)},
			"trip": {"truck": "ABC 1234", "driver": drivers[0],
					 "route": "Lusaka → Ndola",
					 "planned_start_date": add_days(today(), -9),
					 "planned_end_date": add_days(today(), -8),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 5300,
					 "revenue": 14000,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 3200},
						 {"cost_type": "Toll Fees", "planned_amount": 800},
						 {"cost_type": "Driver Allowance", "planned_amount": 1000},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 3050},
						 {"cost_type": "Toll Fees", "actual_amount": 800},
						 {"cost_type": "Driver Allowance", "actual_amount": 1000},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -9), "Lusaka Yard", "Loaded"),
				("Delivered", add_days(today(), -8), "Ndola Mine Site", "On time"),
			],
		},
		{
			"label": "Trip 6: Shoprite - Lusaka to Kitwe (thin margin)",
			"order": {"customer": "Shoprite Zambia", "order_date": add_days(today(), -7),
					  "pickup_location": "Shoprite DC - Lusaka",
					  "delivery_location": "Shoprite Kitwe Store",
					  "cargo_description": "Mixed retail goods - 14 tons", "weight": 14,
					  "requested_delivery_date": add_days(today(), -6)},
			"trip": {"truck": "DEF 4567", "driver": drivers[3],
					 "route": "Lusaka → Kitwe",
					 "planned_start_date": add_days(today(), -7),
					 "planned_end_date": add_days(today(), -6),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 9000,
					 "revenue": 11500,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 6500},
						 {"cost_type": "Toll Fees", "planned_amount": 800},
						 {"cost_type": "Driver Allowance", "planned_amount": 1400},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 6900},
						 {"cost_type": "Toll Fees", "actual_amount": 800},
						 {"cost_type": "Driver Allowance", "actual_amount": 1400},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -7), "Shoprite Lusaka DC", "Loaded"),
				("Delivered", add_days(today(), -6), "Shoprite Kitwe", "On time"),
			],
		},
		{
			"label": "Trip 7: Shoprite - Lusaka to Kitwe #2",
			"order": {"customer": "Shoprite Zambia", "order_date": add_days(today(), -4),
					  "pickup_location": "Shoprite DC - Lusaka",
					  "delivery_location": "Shoprite Kitwe Store",
					  "cargo_description": "Dry goods - 15 tons", "weight": 15,
					  "requested_delivery_date": add_days(today(), -3)},
			"trip": {"truck": "DEF 4567", "driver": drivers[3],
					 "route": "Lusaka → Kitwe",
					 "planned_start_date": add_days(today(), -4),
					 "planned_end_date": add_days(today(), -3),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 9000,
					 "revenue": 11500,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 6500},
						 {"cost_type": "Toll Fees", "planned_amount": 800},
						 {"cost_type": "Driver Allowance", "planned_amount": 1400},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 6400},
						 {"cost_type": "Toll Fees", "actual_amount": 800},
						 {"cost_type": "Driver Allowance", "actual_amount": 1400},
					 ]},
			"action": "complete",
			"checkpoints": [
				("Picked Up", add_days(today(), -4), "Shoprite Lusaka DC", "Loaded"),
				("Delivered", add_days(today(), -3), "Shoprite Kitwe", "On time"),
			],
		},
		{
			"label": "Trip 8: Zambian Breweries - Lusaka to Livingstone (IN PROGRESS)",
			"order": {"customer": "Zambian Breweries", "order_date": add_days(today(), -2),
					  "pickup_location": "ZB Brewery - Lusaka",
					  "delivery_location": "Livingstone Distribution Centre",
					  "cargo_description": "Packaged beverages - 18 tons", "weight": 18,
					  "requested_delivery_date": add_days(today(), 1)},
			"trip": {"truck": "BCD 2345", "driver": drivers[1],
					 "route": "Lusaka → Livingstone",
					 "planned_start_date": add_days(today(), -2),
					 "planned_end_date": today(),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 14000,
					 "revenue": 52 * 480,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 9500},
						 {"cost_type": "Toll Fees", "planned_amount": 1400},
						 {"cost_type": "Driver Allowance", "planned_amount": 1800},
					 ],
					 "actual_costs": [
						 {"cost_type": "Diesel/Fuel", "actual_amount": 4700},
					 ]},
			"action": "start",
			"checkpoints": [
				("Picked Up", add_days(today(), -2), "ZB Lusaka", "Loaded 18 tons"),
				("In Transit", add_days(today(), -1), "Mazabuka", "Overnight stop"),
				("In Transit", today(), "Choma", "ETA Livingstone: 4 hours"),
			],
		},
		{
			"label": "Trip 9: Kasumbalesa Traders - Ndola to DRC border (IN PROGRESS at border)",
			"order": {"customer": "Kasumbalesa Traders", "order_date": add_days(today(), -1),
					  "pickup_location": "Ndola Warehouse",
					  "delivery_location": "Kasumbalesa Border",
					  "cargo_description": "Construction goods - 21 tons", "weight": 21,
					  "requested_delivery_date": today()},
			"trip": {"truck": "CDE 3456", "driver": drivers[3],
					 "route": "Ndola → Kasumbalesa",
					 "planned_start_date": add_days(today(), -1),
					 "planned_end_date": today(),
					 "transaction_currency": SECONDARY_CURRENCY,
					 "exchange_rate": USD_TO_ZMW_RATE,
					 "budget_amount": 1100,
					 "revenue": 1730,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 340},
						 {"cost_type": "Border Fees", "planned_amount": 380},
						 {"cost_type": "Permits", "planned_amount": 200},
						 {"cost_type": "Driver Allowance", "planned_amount": 200},
					 ]},
			"action": "start",
			"checkpoints": [
				("Picked Up", add_days(today(), -1), "Ndola Warehouse", "21 tons loaded"),
				("At Border", today(), "Kasumbalesa Border Post", "In customs queue - est 3hr wait"),
			],
		},
		{
			"label": "Trip 10: Copperbelt Mining - Lusaka to Ndola (PLANNED - tomorrow)",
			"order": {"customer": "Copperbelt Mining Ltd", "order_date": today(),
					  "pickup_location": "Copperbelt Mining - Lusaka Yard",
					  "delivery_location": "Ndola Mine Site",
					  "cargo_description": "Drilling equipment - 26 tons", "weight": 26,
					  "requested_delivery_date": add_days(today(), 2)},
			"trip": {"truck": "ABC 1234", "driver": drivers[0],
					 "route": "Lusaka → Ndola",
					 "planned_start_date": add_days(today(), 1),
					 "planned_end_date": add_days(today(), 2),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 5300,
					 "revenue": 14000,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 3200},
						 {"cost_type": "Toll Fees", "planned_amount": 800},
						 {"cost_type": "Driver Allowance", "planned_amount": 1000},
					 ]},
			"action": "draft",
			"checkpoints": [],
		},
		{
			"label": "Trip 11: Agro Fresh - Lusaka to Chipata (PLANNED - next week)",
			"order": {"customer": "Agro Fresh Zambia", "order_date": today(),
					  "pickup_location": "Agro Fresh Cold Store - Lusaka",
					  "delivery_location": "Chipata DC",
					  "cargo_description": "Fresh produce - 19 tons", "weight": 19,
					  "requested_delivery_date": add_days(today(), 5)},
			"trip": {"truck": "CDE 3456", "driver": drivers[2],
					 "route": "Lusaka → Chipata",
					 "planned_start_date": add_days(today(), 3),
					 "planned_end_date": add_days(today(), 5),
					 "transaction_currency": BASE_CURRENCY, "exchange_rate": 1,
					 "budget_amount": 13000,
					 "revenue": 1200 * 19,
					 "planned_costs": [
						 {"cost_type": "Diesel/Fuel", "planned_amount": 9800},
						 {"cost_type": "Toll Fees", "planned_amount": 1500},
						 {"cost_type": "Driver Allowance", "planned_amount": 1500},
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
		# Back-fill expense_category Link from cost_type string so rows are
		# aligned with the new SRS-aligned model from day one.
		for bucket in ("planned_costs", "actual_costs"):
			for row in trip_data.get(bucket, []):
				if row.get("cost_type") and not row.get("expense_category"):
					row["expense_category"] = row["cost_type"]

		trip = frappe.get_doc({"doctype": "Trip", **trip_data})
		trip.insert(ignore_permissions=True)

		if s["action"] in ("start", "complete"):
			trip.status = "In Progress"
			trip.actual_start_date = trip.planned_start_date
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

		icon = {"Planned": "  ", "Draft": "  ", "In Progress": ">>", "Completed": "OK"}
		print(f"  [{icon.get(trip.status, '??')}] {trip.name} | {trip.customer_name} | {trip.status} | Rev: {trip.revenue} {trip.transaction_currency or ''}")

	frappe.db.commit()
	print(f"  [OK] {len(scenarios)} Orders + Trips created")


def _create_fuel_logs():
	if frappe.db.count("Fuel Log") > 0:
		return

	drivers = [d.name for d in frappe.get_all("Driver", fields=["name"], order_by="creation")]

	logs = [
		# ABC 1234 - efficient driver (Mwansa)
		{"date": add_days(today(), -21), "truck": "ABC 1234", "driver": drivers[0],
		 "liters": 210, "cost_per_liter": 32.50, "odometer_reading": 124000, "fuel_station": "Total - Lusaka South"},
		{"date": add_days(today(), -20), "truck": "ABC 1234", "driver": drivers[0],
		 "liters": 175, "cost_per_liter": 32.80, "odometer_reading": 124320, "fuel_station": "Puma - Ndola"},
		{"date": add_days(today(), -9), "truck": "ABC 1234", "driver": drivers[0],
		 "liters": 225, "cost_per_liter": 32.60, "odometer_reading": 124920, "fuel_station": "Total - Kapiri Mposhi"},
		{"date": add_days(today(), -8), "truck": "ABC 1234", "driver": drivers[0],
		 "liters": 180, "cost_per_liter": 32.90, "odometer_reading": 125240, "fuel_station": "Puma - Ndola"},

		# BCD 2345 - long haul (Chileshe)
		{"date": add_days(today(), -18), "truck": "BCD 2345", "driver": drivers[1],
		 "liters": 330, "cost_per_liter": 32.50, "odometer_reading": 88000, "fuel_station": "Total - Lusaka West"},
		{"date": add_days(today(), -17), "truck": "BCD 2345", "driver": drivers[1],
		 "liters": 280, "cost_per_liter": 33.10, "odometer_reading": 88480, "fuel_station": "Puma - Mazabuka"},
		{"date": add_days(today(), -2), "truck": "BCD 2345", "driver": drivers[1],
		 "liters": 325, "cost_per_liter": 32.70, "odometer_reading": 89150, "fuel_station": "Total - Lusaka"},

		# CDE 3456 - refrigerated (higher consumption)
		{"date": add_days(today(), -14), "truck": "CDE 3456", "driver": drivers[2],
		 "liters": 400, "cost_per_liter": 32.50, "odometer_reading": 66000, "fuel_station": "Puma - Lusaka"},
		{"date": add_days(today(), -12), "truck": "CDE 3456", "driver": drivers[2],
		 "liters": 365, "cost_per_liter": 33.20, "odometer_reading": 66570, "fuel_station": "Total - Nyimba"},

		# DEF 4567 - newer driver (Mulenga)
		{"date": add_days(today(), -7), "truck": "DEF 4567", "driver": drivers[3],
		 "liters": 205, "cost_per_liter": 32.50, "odometer_reading": 45000, "fuel_station": "Total - Lusaka"},
		{"date": add_days(today(), -4), "truck": "DEF 4567", "driver": drivers[3],
		 "liters": 195, "cost_per_liter": 32.80, "odometer_reading": 45360, "fuel_station": "Puma - Kitwe"},
	]

	for l in logs:
		frappe.get_doc({"doctype": "Fuel Log", **l}).insert(ignore_permissions=True)

	print(f"  [OK] {len(logs)} Fuel Logs (4 trucks, Zambia stations)")
