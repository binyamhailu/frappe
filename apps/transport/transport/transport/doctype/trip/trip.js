frappe.ui.form.on("Trip", {
	refresh(frm) {
		// Status-based action buttons
		const startable = ["Planned", "Approved", "Dispatched", "Draft"];
		if (startable.includes(frm.doc.status)) {
			frm.add_custom_button(__("Start Trip"), () => {
				frm.call("start_trip").then(() => frm.reload_doc());
			}, __("Actions"));
		}

		if (frm.doc.status === "In Progress") {
			frm.add_custom_button(__("Mark as Delivered"), () => {
				frm.call("complete_trip").then(() => frm.reload_doc());
			}, __("Actions"));

			// Checkpoint quick-add buttons
			const checkpoints = ["In Transit", "At Border", "At Checkpoint", "Arrived at Destination", "Delayed"];
			checkpoints.forEach((cp) => {
				frm.add_custom_button(__(cp), () => {
					let d = new frappe.ui.Dialog({
						title: __("Add Checkpoint: " + cp),
						fields: [
							{ fieldname: "location", fieldtype: "Data", label: "Location" },
							{ fieldname: "notes", fieldtype: "Data", label: "Notes" },
						],
						primary_action_label: __("Add"),
						primary_action(values) {
							frm.call("add_checkpoint", {
								checkpoint_type: cp,
								location: values.location,
								notes: values.notes,
							}).then(() => {
								d.hide();
								frm.reload_doc();
							});
						},
					});
					d.show();
				}, __("Track"));
			});

			// Log Fuel button
			frm.add_custom_button(__("Log Fuel"), () => {
				frappe.new_doc("Fuel Log", { trip: frm.doc.name, truck: frm.doc.truck, driver: frm.doc.driver });
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
		const status_colors = {
			Planned: "grey",
			Approved: "cyan",
			Dispatched: "orange",
			Draft: "grey",
			"In Progress": "blue",
			Completed: "green",
			Closed: "darkgrey",
			Cancelled: "red",
		};
		if (status_colors[frm.doc.status]) {
			frm.page.set_indicator(__(frm.doc.status), status_colors[frm.doc.status]);
		}

		// Budget status headline
		if (frm.doc.budget_status === "Over Budget") {
			frm.dashboard.set_headline(
				__('<span style="color:red;font-weight:bold;">Over Budget by {0}%</span>',
					[Math.abs(frm.doc.variance_percentage).toFixed(1)])
			);
		} else if (frm.doc.budget_status === "Under Budget") {
			frm.dashboard.set_headline(
				__('<span style="color:green;font-weight:bold;">Under Budget by {0}%</span>',
					[Math.abs(frm.doc.variance_percentage).toFixed(1)])
			);
		}

		// Late delivery warning
		if (frm.doc.is_late) {
			frm.dashboard.set_headline(
				__('<span style="color:red;font-weight:bold;">LATE - Delayed by {0} hours</span>',
					[frm.doc.delay_hours ? frm.doc.delay_hours.toFixed(1) : "?"])
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

	// Auto-fetch rate when route changes
	route(frm) {
		if (frm.doc.customer && frm.doc.route && !frm.doc.revenue) {
			frappe.call({
				method: "transport.transport.doctype.transport_rate_card.transport_rate_card.get_applicable_rate",
				args: { customer: frm.doc.customer, route: frm.doc.route },
				callback(r) {
					if (r.message) {
						frm.set_value("rate_card", r.message.name);
						frappe.show_alert({
							message: __("Rate card {0} applied", [r.message.name]),
							indicator: "green",
						});
					}
				},
			});
		}
	},
});

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
