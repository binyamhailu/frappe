frappe.ui.form.on("Trip", {
	refresh(frm) {
		// Status-based action buttons
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Start Trip"), () => {
				frm.call("start_trip").then(() => frm.reload_doc());
			}, __("Actions"));
		}

		if (frm.doc.status === "In Progress") {
			frm.add_custom_button(__("Mark as Delivered"), () => {
				frm.call("complete_trip").then(() => frm.reload_doc());
			}, __("Actions"));
		}

		if (frm.doc.status === "Completed") {
			frm.add_custom_button(__("Close Trip"), () => {
				frm.call("close_trip").then(() => frm.reload_doc());
			}, __("Actions"));

			if (!frm.doc.sales_invoice) {
				frm.add_custom_button(__("Create Invoice"), () => {
					frm.call("create_sales_invoice").then(() => frm.reload_doc());
				}, __("Actions"));
			}
		}

		// Color the status indicator
		if (frm.doc.status === "Draft") {
			frm.page.set_indicator(__("Draft"), "grey");
		} else if (frm.doc.status === "In Progress") {
			frm.page.set_indicator(__("In Progress"), "blue");
		} else if (frm.doc.status === "Completed") {
			frm.page.set_indicator(__("Completed"), "green");
		} else if (frm.doc.status === "Closed") {
			frm.page.set_indicator(__("Closed"), "darkgrey");
		} else if (frm.doc.status === "Cancelled") {
			frm.page.set_indicator(__("Cancelled"), "red");
		}

		// Budget status indicator
		if (frm.doc.budget_status === "Over Budget") {
			frm.dashboard.set_headline(
				__('<span style="color: red; font-weight: bold;">⚠ Over Budget by {0}%</span>',
					[Math.abs(frm.doc.variance_percentage).toFixed(1)])
			);
		} else if (frm.doc.budget_status === "Under Budget") {
			frm.dashboard.set_headline(
				__('<span style="color: green; font-weight: bold;">✓ Under Budget by {0}%</span>',
					[Math.abs(frm.doc.variance_percentage).toFixed(1)])
			);
		}

		// Lock form if closed
		if (frm.doc.status === "Closed") {
			frm.disable_save();
		}
	},

	transport_order(frm) {
		if (frm.doc.transport_order) {
			frappe.db.get_doc("Transport Order", frm.doc.transport_order).then((order) => {
				frm.set_value("customer", order.customer);
				frm.set_value("customer_name", order.customer_name);
			});
		}
	},
});

// Auto-populate actual cost rows from planned costs
frappe.ui.form.on("Trip Planned Cost", {
	planned_amount(frm) {
		frm.trigger("validate");
	},
});

frappe.ui.form.on("Trip Actual Cost", {
	actual_amount(frm) {
		frm.trigger("validate");
	},
});
