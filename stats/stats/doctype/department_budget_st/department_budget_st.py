# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from stats.constants import BUDGET_EXPENSE_ACCOUNT


class DepartmentBudgetST(Document):
	def validate(self):
		self.calculate_net_balance()

	def calculate_net_balance(self):
		if len(self.account_table)>0:
			for row in self.account_table:
				row.net_balance = (row.approved_amount or 0) + (row.previous_balance or 0)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_budget_account(doctype, txt, searchfield, start, page_len, filters):
	company = erpnext.get_default_company()
	account_list = frappe.db.get_all("Company",filters={"name":company},
							  fields=BUDGET_EXPENSE_ACCOUNT,as_list=0)

	account_name_list = []
	for acct in account_list:
		for budget_account in BUDGET_EXPENSE_ACCOUNT:
			account_name = (acct.get(budget_account),)
			account_name_list.append(account_name)	

	return account_name_list