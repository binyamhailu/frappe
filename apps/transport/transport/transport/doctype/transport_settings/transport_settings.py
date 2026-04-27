import frappe
from frappe import _
from frappe.model.document import Document


class TransportSettings(Document):
	def validate(self):
		if self.default_company:
			company_currency = frappe.db.get_value(
				"Company", self.default_company, "default_currency"
			)
			if company_currency:
				self.base_currency = company_currency


def get_settings():
	"""Shortcut used by cost source DocTypes."""
	return frappe.get_cached_doc("Transport Settings")


def require_account(fieldname):
	"""Return the configured account or raise with a helpful message."""
	settings = get_settings()
	account = settings.get(fieldname)
	if not account:
		frappe.throw(
			_("Transport Settings is missing '{0}'. Configure it under Setup → Transport Settings.").format(
				fieldname.replace("_", " ").title()
			)
		)
	return account
