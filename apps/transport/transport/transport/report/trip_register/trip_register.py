import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Trip"), "fieldname": "name", "fieldtype": "Link", "options": "Trip", "width": 140},
		{"label": _("Transport Order"), "fieldname": "transport_order", "fieldtype": "Link", "options": "Transport Order", "width": 150},
		{"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
		{"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
		{"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Link", "options": "Route", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Planned Start"), "fieldname": "planned_start_date", "fieldtype": "Date", "width": 110},
		{"label": _("Planned End"), "fieldname": "planned_end_date", "fieldtype": "Date", "width": 110},
		{"label": _("Actual Start"), "fieldname": "actual_start_date", "fieldtype": "Date", "width": 110},
		{"label": _("Actual End"), "fieldname": "actual_end_date", "fieldtype": "Date", "width": 110},
		{"label": _("Planned Cost"), "fieldname": "total_planned_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "total_actual_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("t.planned_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("t.planned_start_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	if filters.get("status"):
		conditions.append("t.status = %(status)s")
		values["status"] = filters["status"]

	if filters.get("truck"):
		conditions.append("t.truck = %(truck)s")
		values["truck"] = filters["truck"]

	if filters.get("driver"):
		conditions.append("t.driver = %(driver)s")
		values["driver"] = filters["driver"]

	if filters.get("customer"):
		conditions.append("t.customer = %(customer)s")
		values["customer"] = filters["customer"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT
			t.name, t.transport_order, t.customer_name, t.truck, t.driver, t.route,
			t.status, t.planned_start_date, t.planned_end_date,
			t.actual_start_date, t.actual_end_date,
			t.total_planned_cost, t.total_actual_cost, t.revenue, t.gross_profit
		FROM `tabTrip` t
		WHERE {where_clause}
		ORDER BY t.creation DESC
	""", values, as_dict=True)
