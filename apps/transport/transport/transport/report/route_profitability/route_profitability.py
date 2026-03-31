import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Link", "options": "Route", "width": 200},
		{"label": _("Total Trips"), "fieldname": "total_trips", "fieldtype": "Int", "width": 100},
		{"label": _("Total Revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Profit"), "fieldname": "total_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Avg Profit/Trip"), "fieldname": "avg_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Avg Margin %"), "fieldname": "avg_margin", "fieldtype": "Percent", "width": 110},
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

	conditions.append("route IS NOT NULL")
	conditions.append("route != ''")

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			route,
			COUNT(*) as total_trips,
			SUM(IFNULL(revenue, 0)) as total_revenue,
			SUM(IFNULL(total_actual_cost, 0)) as total_cost,
			SUM(IFNULL(gross_profit, 0)) as total_profit,
			ROUND(AVG(IFNULL(gross_profit, 0)), 2) as avg_profit,
			ROUND(
				CASE WHEN SUM(IFNULL(revenue, 0)) > 0
				THEN (SUM(IFNULL(gross_profit, 0)) / SUM(IFNULL(revenue, 0))) * 100
				ELSE 0 END
			, 2) as avg_margin
		FROM `tabTrip`
		WHERE {where_clause}
		GROUP BY route
		ORDER BY total_profit DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None

	labels = [d.route for d in data]
	profit = [d.total_profit or 0 for d in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Total Profit"), "values": profit}],
		},
		"type": "bar",
		"colors": ["#48BB78"],
	}
