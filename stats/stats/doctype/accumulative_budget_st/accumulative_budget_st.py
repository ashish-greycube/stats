# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccumulativeBudgetST(Document):
	@frappe.whitelist()
	def get_department_budget_requests(self):
		# print('get_department_budget_requests----')
		fetch_accumulative_budget_request = frappe.db.sql("""SELECT	ad.account_name, sum(ad.requested_amount) as requested_amount
													FROM `tabAccounts Details ST` AS ad 
													inner join `tabDepartment Budget ST` AS db on db.name = ad.parent 
													where db.fiscal_year = %s group by ad.account_name""",self.fiscal_year,as_dict=True)
		# print(fetch_accumulative_budget_request, '---fetch_accumulative_budget_request')	
		return fetch_accumulative_budget_request
