frappe.query_reports["Rate Card Summary"] = {
	filters: [
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "route",
			label: __("Route"),
			fieldtype: "Link",
			options: "Route",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nActive\nExpired\nCancelled",
		},
	],
};
