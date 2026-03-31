app_name = "transport"
app_title = "Transport"
app_publisher = "Admin"
app_description = "Transport and Logistics Management"
app_email = "admin@example.com"
app_license = "mit"

required_apps = ["frappe", "erpnext"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "transport",
		"logo": "/assets/transport/images/transport-logo.svg",
		"title": "Transport",
		"route": "/app/transport",
	}
]

# DocType JS
doctype_js = {
	"Trip": "transport/doctype/trip/trip.js",
}

# DocType List JS
doctype_list_js = {
	"Trip": "transport/doctype/trip/trip_list.js",
	"Transport Order": "transport/doctype/transport_order/transport_order_list.js",
}

# DocType Dashboards
override_doctype_dashboards = {
	"Trip": "transport.transport.doctype.trip.trip_dashboard.get_data",
	"Transport Order": "transport.transport.doctype.transport_order.transport_order_dashboard.get_data",
	"Truck": "transport.transport.doctype.truck.truck_dashboard.get_data",
	"Driver": "transport.transport.doctype.driver.driver_dashboard.get_data",
}
