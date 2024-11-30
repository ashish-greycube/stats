# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StatisticRequestST(Document):
	def validate(self):
		self.calculate_costs()

	def calculate_costs(self):
		worker_cost_per_day = frappe.db.get_single_value('Stats Settings ST', 'worker_cost_per_day')
		if not worker_cost_per_day or worker_cost_per_day < 1:
			frappe.throw(_("Please Set Worker Cost Per Day In Stats Settings."))
		else:
			pass

		employee_cost_per_day = frappe.db.get_single_value('Stats Settings ST', 'employee_cost_per_day')
		if not employee_cost_per_day or employee_cost_per_day < 1:
			frappe.throw(_("Please Set Employee Cost Per Day In Stats Settings."))
		else:
			pass

		reservation_cost = frappe.db.get_single_value('Stats Settings ST', 'reservation_cost')
		if not reservation_cost or reservation_cost < 1:
			frappe.throw(_("Please Set Reservation Cost Per Day In Stats Settings."))
		else:
			pass

		self.total_no_team = ((self.number_of_researchers or 0) + (self.number_of_inspectors or 0)
							+ (self.no_of_support_team or 0) + (self.no_of_workers or 0)
							+ (self.no_of_supervisor or 0))
		
		self.workers_cost = ((self.no_of_workers or 0) * (self.no_of_days or 0)) * worker_cost_per_day

		self.estimated_cost = self.total_no_team * employee_cost_per_day * (self.no_of_days or 0)

		self.total_estimated_cost = self.workers_cost + self.estimated_cost

		self.reservation_value = self.total_estimated_cost * (reservation_cost / 100)

		self.final_cost = self.total_estimated_cost + self.reservation_value

		if self.total_no_team and self.total_no_team > 0:
			self.number_of_reserve_workers = self.reservation_value / employee_cost_per_day / self.total_no_team