import frappe
from frappe.utils import flt
from frappe.model.document import Document


class FuelLog(Document):
	def validate(self):
		self.calculate_total_cost()
		self.calculate_efficiency()

	def calculate_total_cost(self):
		self.total_cost = flt(self.liters) * flt(self.cost_per_liter)

	def calculate_efficiency(self):
		if not self.odometer_reading or not self.truck:
			return

		# Get previous fuel log for this truck
		prev = frappe.db.sql("""
			SELECT odometer_reading
			FROM `tabFuel Log`
			WHERE truck = %s AND name != %s AND odometer_reading > 0
			ORDER BY date DESC, creation DESC
			LIMIT 1
		""", (self.truck, self.name or ""), as_dict=True)

		if prev and prev[0].odometer_reading:
			self.km_since_last_fill = flt(self.odometer_reading) - flt(prev[0].odometer_reading)

			if flt(self.liters) > 0 and flt(self.km_since_last_fill) > 0:
				self.consumption_rate = flt(self.km_since_last_fill) / flt(self.liters)
				self.cost_per_km = flt(self.total_cost) / flt(self.km_since_last_fill)
