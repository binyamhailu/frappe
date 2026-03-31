import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 140},
		{"label": _("Total Trips"), "fieldname": "total_trips", "fieldtype": "Int", "width": 100},
		{"label": _("Completed"), "fieldname": "completed_trips", "fieldtype": "Int", "width": 100},
		{"label": _("In Progress"), "fieldname": "in_progress_trips", "fieldtype": "Int", "width": 100},
		{"label": _("Total Revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Profit"), "fieldname": "total_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Avg Profit/Trip"), "fieldname": "avg_profit", "fieldtype": "Currency", "width": 130},
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

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT
			truck,
			COUNT(*) as total_trips,
			SUM(CASE WHEN status IN ('Completed', 'Closed') THEN 1 ELSE 0 END) as completed_trips,
			SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_trips,
			SUM(IFNULL(revenue, 0)) as total_revenue,
			SUM(IFNULL(total_actual_cost, 0)) as total_cost,
			SUM(IFNULL(gross_profit, 0)) as total_profit,
			ROUND(AVG(IFNULL(gross_profit, 0)), 2) as avg_profit
		FROM `tabTrip`
		WHERE {where_clause}
		GROUP BY truck
		ORDER BY total_profit DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None

	labels = [d.truck for d in data]
	revenue = [d.total_revenue or 0 for d in data]
	cost = [d.total_cost or 0 for d in data]
	profit = [d.total_profit or 0 for d in data]

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
