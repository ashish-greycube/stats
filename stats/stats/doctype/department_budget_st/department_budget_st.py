# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document


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
							  fields=["custom_default_business_trip_budget_account","custom_default_business_trip_chargeable_account"],as_list=1)

	account_name_list = []
	for ele in account_list[0]:
		account_name = tuple(map(str, ele.split(', ')))
		account_name_list.append(account_name)
	
	return account_name_list