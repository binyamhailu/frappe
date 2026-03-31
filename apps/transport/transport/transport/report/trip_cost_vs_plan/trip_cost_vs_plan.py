import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Trip"), "fieldname": "trip", "fieldtype": "Link", "options": "Trip", "width": 140},
		{"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
		{"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Total Planned"), "fieldname": "total_planned_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Actual"), "fieldname": "total_actual_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Variance"), "fieldname": "total_variance", "fieldtype": "Currency", "width": 120},
		{"label": _("Variance %"), "fieldname": "variance_percentage", "fieldtype": "Percent", "width": 100},
		{"label": _("Budget Status"), "fieldname": "budget_status", "fieldtype": "Data", "width": 120},
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

	if filters.get("truck"):
		conditions.append("truck = %(truck)s")
		values["truck"] = filters["truck"]

	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT
			name as trip, customer_name, truck, status,
			total_planned_cost, total_actual_cost, total_variance,
			variance_percentage, budget_status
		FROM `tabTrip`
		WHERE {where_clause}
		ORDER BY creation DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None

	labels = [d.trip for d in data[:20]]
	planned = [d.total_planned_cost or 0 for d in data[:20]]
	actual = [d.total_actual_cost or 0 for d in data[:20]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Planned Cost"), "values": planned},
				{"name": _("Actual Cost"), "values": actual},
			],
		},
		"type": "bar",
		"colors": ["#318AD8", "#F47A1F"],
	}
