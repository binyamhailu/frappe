import frappe
from frappe import _
from frappe.model.document import Document


class ExpenseCategory(Document):
	def validate(self):
		self.validate_unique_company_mapping()

	def validate_unique_company_mapping(self):
		seen = set()
		for row in self.mappings or []:
			if row.company in seen:
				frappe.throw(
					_("Duplicate account mapping for company {0}").format(row.company)
				)
			seen.add(row.company)


def get_expense_account(category, company):
	"""Resolve the GL expense account for a given category + company.

	Lookup order:
	1. Expense Category account mapping for this company
	2. Company default_expense_account
	Raises if neither is set — the SRS requires every expense to have a GL target.
	"""
	account = frappe.db.get_value(
		"Expense Category Account",
		{"parent": category, "company": company},
		"expense_account",
	)
	if account:
		return account

	default = frappe.get_cached_value("Company", company, "default_expense_account")
	if default:
		return default

	frappe.throw(
		_("No expense account configured for category {0} in company {1}. "
		  "Add a mapping in Expense Category or set the company's default expense account.").format(
			category, company
		)
	)
