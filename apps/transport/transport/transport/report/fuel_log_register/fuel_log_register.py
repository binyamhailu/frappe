import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Fuel Log"), "fieldname": "name", "fieldtype": "Link", "options": "Fuel Log", "width": 140},
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
		{"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
		{"label": _("Trip"), "fieldname": "trip", "fieldtype": "Link", "options": "Trip", "width": 120},
		{"label": _("Station"), "fieldname": "fuel_station", "fieldtype": "Data", "width": 130},
		{"label": _("Liters"), "fieldname": "liters", "fieldtype": "Float", "precision": 2, "width": 80},
		{"label": _("Cost/Liter"), "fieldname": "cost_per_liter", "fieldtype": "Currency", "width": 100},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Odometer"), "fieldname": "odometer_reading", "fieldtype": "Float", "precision": 0, "width": 100},
		{"label": _("km/Liter"), "fieldname": "consumption_rate", "fieldtype": "Float", "precision": 2, "width": 90},
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
	if filters.get("driver"):
		conditions.append("driver = %(driver)s")
		values["driver"] = filters["driver"]

	where = " AND ".join(conditions) if conditions else "1=1"

	return frappe.db.sql(f"""
		SELECT name, date, truck, driver, trip, fuel_station,
			liters, cost_per_liter, total_cost, odometer_reading, consumption_rate
		FROM `tabFuel Log`
		WHERE {where}
		ORDER BY date DESC
	""", values, as_dict=True)
