# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ContractTypeST(Document):
	def validate(self):
		self.validate_salary_structure_percentage()

	def validate_salary_structure_percentage(self):
		total_percentage = 0
		if len(self.earning) > 0 :
			for ear in self.earning:
				total_percentage = total_percentage + ear.percent

		if len(self.deduction) > 0:
			for ded in self.deduction:
				total_percentage = total_percentage + ded.percent

		if total_percentage > 100:
			frappe.throw(_("Salary Structure Percentage cann't be  greater than 100"))
