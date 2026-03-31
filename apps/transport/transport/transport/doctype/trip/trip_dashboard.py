from frappe import _


def get_data(data=None):
	return {
		"fieldname": "trip",
		"non_standard_fieldnames": {
			"Sales Invoice": "trip",
		},
		"transactions": [
			{
				"label": _("Billing"),
				"items": ["Sales Invoice"],
			},
		],
		"internal_links": {
			"Transport Order": ["transport_order"],
		},
		"internal_and_external_links": {
			"Transport Order": "transport_order",
		},
	}
