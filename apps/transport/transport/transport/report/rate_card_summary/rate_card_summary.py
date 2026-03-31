import frappe
from frappe import _
from frappe.utils import today, add_days, date_diff


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Rate Card"), "fieldname": "name", "fieldtype": "Link", "options": "Transport Rate Card", "width": 130},
		{"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Link", "options": "Route", "width": 180},
		{"label": _("Rate Type"), "fieldname": "rate_type", "fieldtype": "Data", "width": 110},
		{"label": _("Rate"), "fieldname": "rate_value", "fieldtype": "Currency", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80},
		{"label": _("From"), "fieldname": "effective_from", "fieldtype": "Date", "width": 100},
		{"label": _("To"), "fieldname": "effective_to", "fieldtype": "Date", "width": 100},
		{"label": _("Days Left"), "fieldname": "days_left", "fieldtype": "Int", "width": 80},
		{"label": _("Expiry Alert"), "fieldname": "expiry_alert", "fieldtype": "Data", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("route"):
		conditions.append("route = %(route)s")
		values["route"] = filters["route"]

	where = " AND ".join(conditions) if conditions else "1=1"

	data = frappe.db.sql(f"""
		SELECT name, customer_name, route, rate_type,
			rate_per_trip, rate_per_km, rate_per_ton,
			status, effective_from, effective_to
		FROM `tabTransport Rate Card`
		WHERE {where}
		ORDER BY status ASC, effective_to ASC
	""", values, as_dict=True)

	for d in data:
		# Set the display rate value based on type
		if d.rate_type == "Fixed per Trip":
			d.rate_value = d.rate_per_trip
		elif d.rate_type == "Per Km":
			d.rate_value = d.rate_per_km
		else:
			d.rate_value = d.rate_per_ton

		# Calculate days left
		days = date_diff(d.effective_to, today())
		d.days_left = max(days, 0)

		if d.status == "Expired":
			d.expiry_alert = "Expired"
		elif days <= 7:
			d.expiry_alert = "Expiring this week!"
		elif days <= 30:
			d.expiry_alert = "Expiring soon"
		else:
			d.expiry_alert = ""

	return data
