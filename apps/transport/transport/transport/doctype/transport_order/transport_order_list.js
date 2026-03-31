frappe.listview_settings["Transport Order"] = {
	add_fields: ["status", "customer_name"],
	get_indicator: function (doc) {
		const status_map = {
			"Draft": [__("Draft"), "red", "status,=,Draft"],
			"Confirmed": [__("Confirmed"), "blue", "status,=,Confirmed"],
			"In Progress": [__("In Progress"), "orange", "status,=,In Progress"],
			"Completed": [__("Completed"), "green", "status,=,Completed"],
			"Cancelled": [__("Cancelled"), "grey", "status,=,Cancelled"],
		};
		return status_map[doc.status] || [__(doc.status), "grey", "status,=," + doc.status];
	},
};
