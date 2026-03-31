from frappe import _


def get_data(data=None):
	return {
		"fieldname": "transport_order",
		"transactions": [
			{
				"label": _("Trips"),
				"items": ["Trip"],
			},
		],
	}
