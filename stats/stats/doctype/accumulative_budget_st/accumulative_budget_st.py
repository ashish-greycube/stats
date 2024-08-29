# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccumulativeBudgetST(Document):
	def validate(self):
			self.calculate_amount_difference()

	def calculate_amount_difference(self):
		if len(self.account_details) > 0:
			for row in self.account_details:
				row.difference = (row.requested_amount or 0) - (row.approved_amount or 0)

	@frappe.whitelist()
	def get_department_budget_requests(self):
		fetch_accumulative_budget_request = frappe.db.sql("""SELECT	ad.account_name, sum(ad.requested_amount) as requested_amount
													FROM `tabAccounts Details ST` AS ad 
													inner join `tabDepartment Budget ST` AS db on db.name = ad.parent 
													where db.fiscal_year = %s group by ad.account_name""",self.fiscal_year,as_dict=True)
		return fetch_accumulative_budget_request
	
	@frappe.whitelist()
	def get_department_wise_budegt_allocation(self):
		list_a = ["Hello", "World"]
		return list_a
