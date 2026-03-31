import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Trip(Document):
	def validate(self):
		self.validate_transport_order()
		self.calculate_planned_totals()
		self.calculate_actual_costs()
		self.calculate_variance()
		self.calculate_profitability()

	def validate_transport_order(self):
		if self.transport_order:
			order = frappe.get_doc("Transport Order", self.transport_order)
			if order.docstatus == 2:
				frappe.throw(_("Cannot create trip for cancelled Transport Order {0}").format(self.transport_order))

	def calculate_planned_totals(self):
		self.total_planned_cost = sum(flt(row.planned_amount) for row in self.planned_costs)

	def calculate_actual_costs(self):
		# Build a map of planned amounts by cost type
		planned_map = {}
		for row in self.planned_costs:
			planned_map[row.cost_type] = flt(row.planned_amount)

		total_actual = 0
		for row in self.actual_costs:
			row.planned_amount = planned_map.get(row.cost_type, 0)
			row.variance = flt(row.actual_amount) - flt(row.planned_amount)
			total_actual += flt(row.actual_amount)

		self.total_actual_cost = total_actual

	def calculate_variance(self):
		self.total_variance = flt(self.total_actual_cost) - flt(self.total_planned_cost)

		if flt(self.total_planned_cost) > 0:
			self.variance_percentage = (flt(self.total_variance) / flt(self.total_planned_cost)) * 100
		else:
			self.variance_percentage = 0

		# Set budget status
		if flt(self.total_actual_cost) == 0 and flt(self.total_planned_cost) == 0:
			self.budget_status = ""
		elif flt(self.total_variance) < 0:
			self.budget_status = "Under Budget"
		elif flt(self.total_variance) == 0:
			self.budget_status = "On Budget"
		else:
			self.budget_status = "Over Budget"

	def calculate_profitability(self):
		self.gross_profit = flt(self.revenue) - flt(self.total_actual_cost)
		if flt(self.revenue) > 0:
			self.profit_margin = (flt(self.gross_profit) / flt(self.revenue)) * 100
		else:
			self.profit_margin = 0

	def before_save(self):
		# Restrict editing after closure
		if self.get_doc_before_save():
			old_status = self.get_doc_before_save().status
			if old_status == "Closed" and self.status == "Closed":
				frappe.throw(_("Trip {0} is closed. No further edits allowed.").format(self.name))

	@frappe.whitelist()
	def start_trip(self):
		if self.status != "Draft":
			frappe.throw(_("Only Draft trips can be started"))
		self.status = "In Progress"
		self.actual_start_date = frappe.utils.today()
		self.save()
		frappe.msgprint(_("Trip {0} started").format(self.name), indicator="blue")

	@frappe.whitelist()
	def complete_trip(self):
		if self.status != "In Progress":
			frappe.throw(_("Only In Progress trips can be completed"))
		self.status = "Completed"
		self.actual_end_date = frappe.utils.today()
		self.delivery_confirmation_date = frappe.utils.today()
		self.save()
		frappe.msgprint(_("Trip {0} completed").format(self.name), indicator="green")

	@frappe.whitelist()
	def close_trip(self):
		if self.status != "Completed":
			frappe.throw(_("Only Completed trips can be closed"))
		self.status = "Closed"
		self.save()
		frappe.msgprint(_("Trip {0} closed").format(self.name), indicator="green")

	@frappe.whitelist()
	def create_sales_invoice(self):
		if not self.revenue:
			frappe.throw(_("Please set the Revenue (Transport Fee) before creating an invoice"))

		if self.sales_invoice:
			frappe.throw(_("Sales Invoice {0} already exists for this trip").format(self.sales_invoice))

		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.due_date = frappe.utils.add_days(frappe.utils.today(), 30)

		si.append("items", {
			"item_name": f"Transport Service - {self.name}",
			"description": f"Transport service for Trip {self.name} ({self.transport_order})",
			"qty": 1,
			"rate": self.revenue,
			"income_account": frappe.get_cached_value("Company",
				frappe.defaults.get_user_default("Company"),
				"default_income_account"
			),
		})

		si.flags.ignore_permissions = True
		si.flags.ignore_mandatory = True
		si.insert()

		self.sales_invoice = si.name
		self.save()

		frappe.msgprint(
			_("Sales Invoice {0} created").format(
				f'<a href="/app/sales-invoice/{si.name}">{si.name}</a>'
			),
			indicator="green",
		)

		return si.name
