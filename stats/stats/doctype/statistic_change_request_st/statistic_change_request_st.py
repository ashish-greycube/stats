# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class StatisticChangeRequestST(Document):
	def on_submit(self):
		self.set_new_values_in_statistic_request()

	def set_new_values_in_statistic_request(self):
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'number_of_researchers',self.new_number_of_researchers)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'number_of_inspectors',self.new_number_of_inspectors)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'no_of_support_team',self.new_no_of_support_team)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'no_of_workers',self.new_no_of_workers)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'no_of_supervisor',self.new_no_of_supervisor)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'no_of_days',self.new_no_of_days)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'statistics_method',self.new_statistics_method)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'planned_start_date',self.new_planned_start_date)
		frappe.db.set_value("Statistic Request ST", self.statistic_request_reference, 'planned_end_date',self.new_planned_end_date)
		frappe.msgprint(_("All 9 feilds are updated with new values"))