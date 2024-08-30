# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from stats.constants import BUDGET_EXPENSE_ACCOUNT
from frappe import _
from frappe.utils import get_link_to_form

class DepartmentBudgetST(Document):
	def validate(self):
		self.calculate_net_balance()

	def on_cancel(self):
		for row in self.account_table:
			if frappe.db.exists("Department Wise Budget Allocation Details ST", {"department_acct_details_name": row.name}):
				frappe.throw(_("You Cann't delete this department budget because of Accumulative Budget is created."))

	def calculate_net_balance(self):
		if len(self.account_table)>0:
			for row in self.account_table:
				net_balance = (row.approved_amount or 0) + (row.previous_balance or 0)
				frappe.db.set_value(row.doctype, row.name, 'net_balance', net_balance)
				print(row.net_balance ,'---row.net_balance ')
			# self.save(ignore_permissions=True)

	def on_update_after_submit(self):
		self.calculate_net_balance()
		self.create_budget()
		print('on_update_after_submit===', self.name)

	def create_budget(self):
		print('create_budget')
		for ac in self.account_table:
			budget_doc = frappe.db.get_all('Budget', filters={'cost_center':self.cost_center, 'fiscal_year':self.fiscal_year}, fields=['name'])
			print(budget_doc, '---budget_doc')
			if len(budget_doc) > 0 :
				for budget in budget_doc:
					if frappe.db.exists("Budget Account", {'account': ac.budget_expense_account, 'parent': budget.name}):
						frappe.msgprint(_("Budget {0} Already Exists".format(get_link_to_form('Budget No', budget.name))), alert=True)
					# if budget.accounts[0].account == ac.budget_expense_account:
						print('budget already exists')
						return
			else:
				new_budget = frappe.new_doc('Budget')
				new_budget.cost_center = self.cost_center
				new_budget.fiscal_year = self.fiscal_year
				row = new_budget.append('accounts',{})
				row.account = ac.budget_expense_account
				row.budget_amount = ac.net_balance

				new_budget.submit()
				frappe.msgprint(_("Budget {0} is created."
					  .format(get_link_to_form('Budget No', new_budget.name))), alert=True)
				print(new_budget.name ,'------new_budget')

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