frappe.pages["transport-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Transport Dashboard",
		single_column: true,
	});

	page.main.html(`
		<div class="transport-dashboard" style="padding: 15px;">
			<div class="row kpi-cards" style="margin-bottom: 20px;"></div>
			<div class="row" style="margin-bottom: 20px;">
				<div class="col-md-8">
					<div class="profit-chart-container frappe-card" style="padding: 15px; height: 350px;"></div>
				</div>
				<div class="col-md-4">
					<div class="cost-chart-container frappe-card" style="padding: 15px; height: 350px;"></div>
				</div>
			</div>
			<div class="row">
				<div class="col-md-12">
					<div class="recent-trips-container frappe-card" style="padding: 15px;">
						<h5 style="margin-bottom: 15px;">Recent Trips</h5>
						<div class="recent-trips-table"></div>
					</div>
				</div>
			</div>
		</div>
	`);

	load_dashboard(page);
};

function load_dashboard(page) {
	frappe.call({
		method: "transport.transport.page.transport_dashboard.transport_dashboard.get_dashboard_data",
		callback: function (r) {
			if (r.message) {
				render_kpis(page, r.message.kpis);
				render_profit_chart(page, r.message.profit_trend);
				render_cost_chart(page, r.message.cost_breakdown);
				render_recent_trips(page, r.message.recent_trips);
			}
		},
	});
}

function render_kpis(page, kpis) {
	let cards_html = "";
	const card_configs = [
		{ label: "Total Trips", key: "total_trips", color: "#318AD8", icon: "truck" },
		{ label: "Active Trips", key: "active_trips", color: "#F47A1F", icon: "play" },
		{ label: "Completed Trips", key: "completed_trips", color: "#48BB78", icon: "check" },
		{ label: "Total Revenue", key: "total_revenue", color: "#805AD5", icon: "dollar-sign", is_currency: true },
		{ label: "Total Cost", key: "total_cost", color: "#E53E3E", icon: "credit-card", is_currency: true },
		{ label: "Total Profit", key: "total_profit", color: "#38A169", icon: "trending-up", is_currency: true },
	];

	card_configs.forEach((c) => {
		let value = kpis[c.key] || 0;
		if (c.is_currency) {
			value = format_currency(value);
		}
		cards_html += `
			<div class="col-sm-6 col-md-4 col-lg-2" style="margin-bottom: 10px;">
				<div class="frappe-card" style="padding: 15px; border-left: 4px solid ${c.color}; height: 100%;">
					<div style="font-size: 12px; color: #8d99a6; margin-bottom: 5px;">${c.label}</div>
					<div style="font-size: 20px; font-weight: bold; color: ${c.color};">${value}</div>
				</div>
			</div>
		`;
	});

	page.main.find(".kpi-cards").html(cards_html);
}

function render_profit_chart(page, data) {
	if (!data || !data.labels.length) {
		page.main.find(".profit-chart-container").html("<p class='text-muted'>No data available</p>");
		return;
	}

	new frappe.Chart(page.main.find(".profit-chart-container")[0], {
		title: "Daily Profit Trend (Last 30 Days)",
		data: {
			labels: data.labels,
			datasets: [
				{ name: "Revenue", values: data.revenue },
				{ name: "Profit", values: data.profit },
			],
		},
		type: "line",
		height: 280,
		colors: ["#318AD8", "#48BB78"],
		lineOptions: { regionFill: 1 },
	});
}

function render_cost_chart(page, data) {
	if (!data || !data.labels.length) {
		page.main.find(".cost-chart-container").html("<p class='text-muted'>No data available</p>");
		return;
	}

	new frappe.Chart(page.main.find(".cost-chart-container")[0], {
		title: "Cost Breakdown",
		data: {
			labels: data.labels,
			datasets: [{ values: data.values }],
		},
		type: "pie",
		height: 280,
		colors: ["#318AD8", "#F47A1F", "#48BB78", "#ED8936", "#9F7AEA", "#E53E3E", "#38B2AC"],
	});
}

function render_recent_trips(page, trips) {
	if (!trips || !trips.length) {
		page.main.find(".recent-trips-table").html("<p class='text-muted'>No trips yet</p>");
		return;
	}

	let html = `<table class="table table-bordered table-hover" style="font-size: 13px;">
		<thead>
			<tr>
				<th>Trip</th>
				<th>Customer</th>
				<th>Truck</th>
				<th>Status</th>
				<th>Revenue</th>
				<th>Cost</th>
				<th>Profit</th>
			</tr>
		</thead>
		<tbody>`;

	trips.forEach((t) => {
		let status_color = {
			Draft: "grey",
			"In Progress": "blue",
			Completed: "green",
			Closed: "darkgrey",
			Cancelled: "red",
		};
		let color = status_color[t.status] || "grey";

		html += `<tr>
			<td><a href="/app/trip/${t.name}">${t.name}</a></td>
			<td>${t.customer_name || ""}</td>
			<td>${t.truck || ""}</td>
			<td><span class="indicator-pill ${color}">${t.status}</span></td>
			<td>${format_currency(t.revenue || 0)}</td>
			<td>${format_currency(t.total_actual_cost || 0)}</td>
			<td style="color: ${(t.gross_profit || 0) >= 0 ? "green" : "red"}; font-weight: bold;">
				${format_currency(t.gross_profit || 0)}
			</td>
		</tr>`;
	});

	html += "</tbody></table>";
	page.main.find(".recent-trips-table").html(html);
}
