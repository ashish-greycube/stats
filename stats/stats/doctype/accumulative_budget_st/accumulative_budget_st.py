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
				row.difference = (row.total_requested_amount or 0) - (row.total_approved_amount or 0)

	@frappe.whitelist()
	def get_department_budget_requests(self):
		fetch_accumulative_budget_request = frappe.db.sql("""SELECT	ad.budget_expense_account, sum(ad.requested_amount) as total_requested_amount
													FROM `tabAccounts Details ST` AS ad 
													inner join `tabDepartment Budget ST` AS db on db.name = ad.parent 
													where db.fiscal_year = %s and db.docstatus = 1 
													group by ad.budget_expense_account""",self.fiscal_year,as_dict=True)
		return fetch_accumulative_budget_request
	
	@frappe.whitelist()
	def get_department_wise_budegt_allocation(self):
		accumulative_budget_request=self.account_details
		department_and_account_budget_requests=self.get_department_and_account_budget_requests()

		for budget_amount in department_and_account_budget_requests:
			for acct_amount in accumulative_budget_request:
				if budget_amount['budget_expense_account']==acct_amount.budget_expense_account:
					budget_amount['total_requested_amount']=acct_amount.total_requested_amount
					budget_amount['approved_amount']= (budget_amount['requested_amount']/acct_amount.total_requested_amount)*acct_amount.total_approved_amount
					break
		return department_and_account_budget_requests


	@frappe.whitelist()
	def get_department_and_account_budget_requests(self):
		department_and_account_budget_requests = frappe.db.sql("""SELECT
					db.name as department_budget_name ,db.main_department ,
					ad.name as department_acct_details_name ,ad.budget_expense_account,
					0 as total_requested_amount, ad.requested_amount , 0 as approved_amount
				FROM
					`tabAccounts Details ST` ad
				inner join `tabDepartment Budget ST` db on
					db.name = ad.parent
				where db.fiscal_year = %s and db.docstatus = 1 """,self.fiscal_year,as_dict=True)
		return department_and_account_budget_requests	