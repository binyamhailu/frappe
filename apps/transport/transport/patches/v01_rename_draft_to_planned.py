"""Rename legacy Trip status 'Draft' to 'Planned'.

Aligns with SRS TRIP-002 which defines the canonical status set as
Planned / Approved / Dispatched / In Progress / Completed / Closed / Cancelled.
Existing 'Draft' rows are rewritten to 'Planned' so the new Select options
remain valid. Safe to run multiple times.
"""
import frappe


def execute():
	if not frappe.db.table_exists("Trip"):
		return
	frappe.db.sql("""UPDATE `tabTrip` SET status = 'Planned' WHERE status = 'Draft'""")
	frappe.db.commit()
