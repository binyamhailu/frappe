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
		{"label": _("Fill-ups"), "fieldname": "fill_count", "fieldtype": "Int", "width": 80},
		{"label": _("Total Liters"), "fieldname": "total_liters", "fieldtype": "Float", "precision": 1, "width": 110},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Avg Cost/Liter"), "fieldname": "avg_cost_per_liter", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Km"), "fieldname": "total_km", "fieldtype": "Float", "precision": 0, "width": 100},
		{"label": _("Avg km/Liter"), "fieldname": "avg_km_per_liter", "fieldtype": "Float", "precision": 2, "width": 110},
		{"label": _("Avg Cost/Km"), "fieldname": "avg_cost_per_km", "fieldtype": "Currency", "width": 110},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("truck"):
		conditions.append("truck = %(truck)s")
		values["truck"] = filters["truck"]

	where = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT
			truck,
			COUNT(*) as fill_count,
			ROUND(SUM(IFNULL(liters, 0)), 1) as total_liters,
			SUM(IFNULL(total_cost, 0)) as total_cost,
			ROUND(AVG(IFNULL(cost_per_liter, 0)), 2) as avg_cost_per_liter,
			ROUND(SUM(IFNULL(km_since_last_fill, 0)), 0) as total_km,
			ROUND(
				CASE WHEN SUM(IFNULL(liters, 0)) > 0
				THEN SUM(IFNULL(km_since_last_fill, 0)) / SUM(IFNULL(liters, 0))
				ELSE 0 END
			, 2) as avg_km_per_liter,
			ROUND(
				CASE WHEN SUM(IFNULL(km_since_last_fill, 0)) > 0
				THEN SUM(IFNULL(total_cost, 0)) / SUM(IFNULL(km_since_last_fill, 0))
				ELSE 0 END
			, 2) as avg_cost_per_km
		FROM `tabFuel Log`
		WHERE {where}
		GROUP BY truck
		ORDER BY total_cost DESC
	""", values, as_dict=True)


def get_chart(data):
	if not data:
		return None
	return {
		"data": {
			"labels": [d.truck for d in data],
			"datasets": [
				{"name": _("Total Cost"), "values": [d.total_cost or 0 for d in data]},
				{"name": _("Total Liters"), "values": [d.total_liters or 0 for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#E53E3E", "#318AD8"],
	}
