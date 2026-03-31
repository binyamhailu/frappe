from frappe import _


def get_data(data=None):
	return {
		"fieldname": "truck",
		"transactions": [
			{
				"label": _("Operations"),
				"items": ["Trip"],
			},
			{
				"label": _("Drivers"),
				"items": ["Driver"],
			},
		],
	}
