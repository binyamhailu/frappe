import frappe
from frappe import _
from frappe.utils import getdate, today
from frappe.model.document import Document


class TransportRateCard(Document):
	def validate(self):
		self.validate_dates()
		self.validate_rate()
		self.check_overlap()
		self.update_status()

	def validate_dates(self):
		if getdate(self.effective_to) < getdate(self.effective_from):
			frappe.throw(_("Effective To date must be after Effective From date"))

	def validate_rate(self):
		if self.rate_type == "Fixed per Trip" and not self.rate_per_trip:
			frappe.throw(_("Rate per Trip is required for Fixed per Trip rate type"))
		elif self.rate_type == "Per Km" and not self.rate_per_km:
			frappe.throw(_("Rate per Km is required for Per Km rate type"))
		elif self.rate_type == "Per Ton" and not self.rate_per_ton:
			frappe.throw(_("Rate per Ton is required for Per Ton rate type"))

	def check_overlap(self):
		overlapping = frappe.db.sql("""
			SELECT name FROM `tabTransport Rate Card`
			WHERE customer = %s AND route = %s AND status = 'Active'
			AND name != %s
			AND effective_from <= %s AND effective_to >= %s
		""", (self.customer, self.route, self.name or "",
			  self.effective_to, self.effective_from))

		if overlapping:
			frappe.throw(
				_("Overlapping active rate card {0} exists for this customer and route").format(
					overlapping[0][0]
				)
			)

	def update_status(self):
		if self.status == "Cancelled":
			return
		if getdate(self.effective_to) < getdate(today()):
			self.status = "Expired"
		else:
			self.status = "Active"


@frappe.whitelist()
def get_applicable_rate(customer, route, date=None):
	"""Get the active rate card for a customer + route combination."""
	if not date:
		date = today()

	rate_card = frappe.db.sql("""
		SELECT name, rate_type, rate_per_trip, rate_per_km, rate_per_ton
		FROM `tabTransport Rate Card`
		WHERE customer = %s AND route = %s AND status = 'Active'
		AND effective_from <= %s AND effective_to >= %s
		ORDER BY effective_from DESC
		LIMIT 1
	""", (customer, route, date, date), as_dict=True)

	if rate_card:
		return rate_card[0]
	return None
