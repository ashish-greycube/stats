# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date

class EmployeeContractST(Document):
	def validate(self):
		self.validate_trial_period()

	def validate_trial_period(self):
		if self.contract_start_date:
			self.trial_period_end_date = add_to_date(self.contract_start_date, months=3)
			if self.test_period_renewed == "Yes":
				self.end_of_new_test_period = add_to_date(self.trial_period_end_date, months=3)
			else:
				self.end_of_new_test_period = None

@frappe.whitelist()
def get_salary_details(parent, parenttype):

	earning = frappe.get_all(
		"Earning ST",
		fields=[
			"earning",
			"value",
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	deduction = frappe.get_all(
		"Deduction ST",
		fields=[
			"deduction",
			"value",
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	return earning, deduction