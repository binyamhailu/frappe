import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Trip"), "fieldname": "name", "fieldtype": "Link", "options": "Trip", "width": 140},
		{"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
		{"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Link", "options": "Route", "width": 160},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Cost"), "fieldname": "total_actual_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Gross Profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "width": 120},
		{"label": _("Margin %"), "fieldname": "profit_margin", "fieldtype": "Percent", "width": 100},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("planned_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("planned_start_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters["customer"]

	if filters.get("truck"):
		conditions.append("truck = %(truck)s")
		values["truck"] = filters["truck"]

	conditions.append("revenue > 0")

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			name, customer_name, truck, route,
			revenue, total_actual_cost, gross_profit, profit_margin
		FROM `tabTrip`
		WHERE {where_clause}
		ORDER BY gross_profit DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None

	labels = [d.name for d in data[:15]]
	revenue = [d.revenue or 0 for d in data[:15]]
	cost = [d.total_actual_cost or 0 for d in data[:15]]
	profit = [d.gross_profit or 0 for d in data[:15]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Revenue"), "values": revenue},
				{"name": _("Cost"), "values": cost},
				{"name": _("Profit"), "values": profit},
			],
		},
		"type": "bar",
		"colors": ["#318AD8", "#F47A1F", "#48BB78"],
	}
