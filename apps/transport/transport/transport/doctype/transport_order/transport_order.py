import frappe
from frappe.model.document import Document


class TransportOrder(Document):
	def validate(self):
		self.update_status_from_trips()

	def update_status_from_trips(self):
		if self.docstatus != 1:
			return

		trips = frappe.get_all(
			"Trip",
			filters={"transport_order": self.name},
			fields=["status"],
		)

		if not trips:
			return

		statuses = [t.status for t in trips]

		if all(s in ("Completed", "Closed") for s in statuses):
			self.status = "Completed"
		elif any(s == "In Progress" for s in statuses):
			self.status = "In Progress"
		elif all(s == "Cancelled" for s in statuses):
			self.status = "Cancelled"

	def on_submit(self):
		self.status = "Confirmed"

	def on_cancel(self):
		self.status = "Cancelled"
