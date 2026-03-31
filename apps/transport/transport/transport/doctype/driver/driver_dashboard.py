from frappe import _


def get_data(data=None):
	return {
		"fieldname": "driver",
		"transactions": [
			{
				"label": _("Operations"),
				"items": ["Trip"],
			},
		],
	}
