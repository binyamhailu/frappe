import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, now_datetime, time_diff_in_hours


class Trip(Document):
	def validate(self):
		self.validate_transport_order()
		self.fetch_rate_card()
		self.calculate_planned_totals()
		self.calculate_actual_costs()
		self.calculate_variance()
		self.calculate_profitability()
		self.update_last_checkpoint()
		self.check_late_delivery()

	def validate_transport_order(self):
		if self.transport_order:
			order = frappe.get_doc("Transport Order", self.transport_order)
			if order.docstatus == 2:
				frappe.throw(_("Cannot create trip for cancelled Transport Order {0}").format(self.transport_order))

	def fetch_rate_card(self):
		"""Auto-fetch rate from active rate card if customer + route set and no revenue yet."""
		if self.customer and self.route and not flt(self.revenue):
			from transport.transport.doctype.transport_rate_card.transport_rate_card import get_applicable_rate
			rate = get_applicable_rate(self.customer, self.route)
			if rate:
				self.rate_card = rate.name
				if rate.rate_type == "Fixed per Trip":
					self.rate_applied = flt(rate.rate_per_trip)
					self.revenue = flt(rate.rate_per_trip)
				elif rate.rate_type == "Per Km":
					distance = frappe.db.get_value("Route", self.route, "estimated_distance_km") or 0
					self.rate_applied = flt(rate.rate_per_km) * flt(distance)
					self.revenue = self.rate_applied
				elif rate.rate_type == "Per Ton":
					weight = frappe.db.get_value("Transport Order", self.transport_order, "weight") or 0
					self.rate_applied = flt(rate.rate_per_ton) * flt(weight)
					self.revenue = self.rate_applied

	def calculate_planned_totals(self):
		self.total_planned_cost = sum(flt(row.planned_amount) for row in self.planned_costs)

	def calculate_actual_costs(self):
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

	def update_last_checkpoint(self):
		if self.checkpoints:
			last = self.checkpoints[-1]
			self.last_checkpoint = f"{last.checkpoint_type} - {last.location or ''}"
		else:
			self.last_checkpoint = ""

	def check_late_delivery(self):
		if self.planned_end_date and self.status in ("In Progress", "Completed", "Closed"):
			if self.actual_end_date:
				if getdate(self.actual_end_date) > getdate(self.planned_end_date):
					self.is_late = 1
					self.delay_hours = time_diff_in_hours(
						f"{self.actual_end_date} 23:59:59",
						f"{self.planned_end_date} 23:59:59"
					)
				else:
					self.is_late = 0
					self.delay_hours = 0
			elif self.status == "In Progress" and getdate(today()) > getdate(self.planned_end_date):
				self.is_late = 1
				self.delay_hours = time_diff_in_hours(
					now_datetime(),
					f"{self.planned_end_date} 23:59:59"
				)

	def before_save(self):
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
		self.append("checkpoints", {
			"checkpoint_type": "Picked Up",
			"timestamp": now_datetime(),
			"location": frappe.db.get_value("Transport Order", self.transport_order, "pickup_location") or "",
			"notes": "Trip started",
		})
		self.save()
		frappe.msgprint(_("Trip {0} started").format(self.name), indicator="blue")

	@frappe.whitelist()
	def complete_trip(self):
		if self.status != "In Progress":
			frappe.throw(_("Only In Progress trips can be completed"))
		self.status = "Completed"
		self.actual_end_date = frappe.utils.today()
		self.delivery_confirmation_date = frappe.utils.today()
		self.append("checkpoints", {
			"checkpoint_type": "Delivered",
			"timestamp": now_datetime(),
			"location": frappe.db.get_value("Transport Order", self.transport_order, "delivery_location") or "",
			"notes": "Trip completed - cargo delivered",
		})
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
	def add_checkpoint(self, checkpoint_type, location=None, notes=None):
		self.append("checkpoints", {
			"checkpoint_type": checkpoint_type,
			"timestamp": now_datetime(),
			"location": location or "",
			"notes": notes or "",
		})
		self.save()
		frappe.msgprint(_("Checkpoint '{0}' added").format(checkpoint_type), indicator="blue")

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
