import frappe
from frappe.utils import add_days, today, getdate


@frappe.whitelist()
def get_dashboard_data():
	return {
		"kpis": get_kpis(),
		"profit_trend": get_profit_trend(),
		"cost_breakdown": get_cost_breakdown(),
		"recent_trips": get_recent_trips(),
	}


def get_kpis():
	data = frappe.db.sql("""
		SELECT
			COUNT(*) as total_trips,
			SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as active_trips,
			SUM(CASE WHEN status IN ('Completed', 'Closed') THEN 1 ELSE 0 END) as completed_trips,
			SUM(IFNULL(revenue, 0)) as total_revenue,
			SUM(IFNULL(total_actual_cost, 0)) as total_cost,
			SUM(IFNULL(gross_profit, 0)) as total_profit
		FROM `tabTrip`
	""", as_dict=True)

	return data[0] if data else {}


def get_profit_trend():
	from_date = add_days(today(), -30)

	data = frappe.db.sql("""
		SELECT
			DATE(planned_start_date) as date,
			SUM(IFNULL(revenue, 0)) as revenue,
			SUM(IFNULL(gross_profit, 0)) as profit
		FROM `tabTrip`
		WHERE planned_start_date >= %s
		GROUP BY DATE(planned_start_date)
		ORDER BY date
	""", from_date, as_dict=True)

	labels = [str(d.date) for d in data]
	revenue = [float(d.revenue or 0) for d in data]
	profit = [float(d.profit or 0) for d in data]

	return {"labels": labels, "revenue": revenue, "profit": profit}


def get_cost_breakdown():
	data = frappe.db.sql("""
		SELECT
			cost_type,
			SUM(IFNULL(actual_amount, 0)) as total
		FROM `tabTrip Actual Cost`
		GROUP BY cost_type
		ORDER BY total DESC
	""", as_dict=True)

	labels = [d.cost_type for d in data]
	values = [float(d.total or 0) for d in data]

	return {"labels": labels, "values": values}


def get_recent_trips():
	return frappe.db.sql("""
		SELECT
			name, customer_name, truck, status,
			revenue, total_actual_cost, gross_profit
		FROM `tabTrip`
		ORDER BY creation DESC
		LIMIT 20
	""", as_dict=True)
