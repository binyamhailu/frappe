from frappe import _


def get_data(data=None):
	return {
		"fieldname": "fuel_log",
		"internal_links": {
			"Trip": ["trip"],
			"Truck": ["truck"],
		},
	}
