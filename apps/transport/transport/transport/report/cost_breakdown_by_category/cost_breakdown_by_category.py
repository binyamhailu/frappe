import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Cost Type"), "fieldname": "cost_type", "fieldtype": "Data", "width": 160},
		{"label": _("Total Planned"), "fieldname": "total_planned", "fieldtype": "Currency", "width": 140},
		{"label": _("Total Actual"), "fieldname": "total_actual", "fieldtype": "Currency", "width": 140},
		{"label": _("Total Variance"), "fieldname": "total_variance", "fieldtype": "Currency", "width": 140},
		{"label": _("Trip Count"), "fieldname": "trip_count", "fieldtype": "Int", "width": 100},
		{"label": _("Avg per Trip"), "fieldname": "avg_per_trip", "fieldtype": "Currency", "width": 130},
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

	if filters.get("truck"):
		conditions.append("t.truck = %(truck)s")
		values["truck"] = filters["truck"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT
			ac.cost_type,
			SUM(IFNULL(ac.planned_amount, 0)) as total_planned,
			SUM(IFNULL(ac.actual_amount, 0)) as total_actual,
			SUM(IFNULL(ac.variance, 0)) as total_variance,
			COUNT(DISTINCT t.name) as trip_count,
			ROUND(AVG(IFNULL(ac.actual_amount, 0)), 2) as avg_per_trip
		FROM `tabTrip Actual Cost` ac
		JOIN `tabTrip` t ON t.name = ac.parent
		WHERE {where_clause}
		GROUP BY ac.cost_type
		ORDER BY total_actual DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None

	labels = [d.cost_type for d in data]
	values = [d.total_actual or 0 for d in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Actual Cost"), "values": values}],
		},
		"type": "pie",
		"colors": ["#318AD8", "#F47A1F", "#48BB78", "#ED8936", "#9F7AEA", "#E53E3E", "#38B2AC"],
	}
