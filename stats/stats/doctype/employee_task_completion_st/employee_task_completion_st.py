# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeTaskCompletionST(Document):
	def validate(self):
		self.validate_approved_days()
	
	def validate_approved_days(self):
		print(self.no_of_days,self.approved_days,"days")
		if self.no_of_days and self.approved_days:
			print(self.no_of_days,self.approved_days,"days")
			if self.approved_days > self.no_of_days:
				frappe.throw(_("Approved days cannot be greater than no of days"))
