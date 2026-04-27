import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Driver(Document):
	def validate(self):
		self.warn_on_expired_license()

	def warn_on_expired_license(self):
		if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
			# Warning rather than hard-throw on the Driver record itself;
			# hard enforcement happens at trip assignment time.
			frappe.msgprint(
				_("Driver {0}'s license expired on {1}.").format(
					self.driver_name, self.license_expiry
				),
				indicator="orange",
				alert=True,
			)
