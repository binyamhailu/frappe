frappe.listview_settings["Trip"] = {
	add_fields: ["status", "budget_status", "total_planned_cost", "total_actual_cost", "gross_profit"],
	get_indicator: function (doc) {
		const status_map = {
			"Draft": [__("Draft"), "grey", "status,=,Draft"],
			"In Progress": [__("In Progress"), "blue", "status,=,In Progress"],
			"Completed": [__("Completed"), "green", "status,=,Completed"],
			"Closed": [__("Closed"), "darkgrey", "status,=,Closed"],
			"Cancelled": [__("Cancelled"), "red", "status,=,Cancelled"],
		};
		return status_map[doc.status] || [__(doc.status), "grey", "status,=," + doc.status];
	},
	formatters: {
		budget_status: function (value) {
			if (value === "Over Budget") {
				return `<span class="text-danger font-weight-bold">${value}</span>`;
			} else if (value === "Under Budget") {
				return `<span class="text-success font-weight-bold">${value}</span>`;
			}
			return value || "";
		},
		gross_profit: function (value) {
			if (value < 0) {
				return `<span class="text-danger">${format_currency(value)}</span>`;
			}
			return format_currency(value || 0);
		},
	},
};
