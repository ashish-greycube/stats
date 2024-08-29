# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DepartmentBudgetST(Document):
	def validate(self):
		self.calculate_net_balance()

	def calculate_net_balance(self):
		if len(self.account_table)>0:
			for row in self.account_table:
				row.net_balance = (row.approved_amount or 0) + (row.previous_balance or 0)
