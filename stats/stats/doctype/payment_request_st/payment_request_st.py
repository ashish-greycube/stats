# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form,today
from frappe.model.document import Document


class PaymentRequestST(Document):
	def on_submit(self):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = today()
		
		accounts = []
		employee_detais = frappe.db.sql("""
				SELECT
				main_department,
				SUM(amount) as amount
			FROM
				`tabEmployee Details For Payment ST`
			WHERE
				parent = %s
			GROUP By
				main_department
		""",self.name,as_dict=1)
		print(employee_detais,"employee_detais")

		employee_total_amount = 0
		company = erpnext.get_default_company()
		if len(employee_detais)>0:
			company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
			for detail_row in employee_detais:
				employee_total_amount = employee_total_amount + detail_row.amount
				department_cost_center = frappe.db.get_value("Department",detail_row.main_department,"custom_department_cost_center")
				accounts_row = {
					"account":company_business_trip_budget_expense_account,
					"cost_center":department_cost_center,
					"department":detail_row.main_department,
					"debit_in_account_currency":detail_row.amount,
				}
				accounts.append(accounts_row)

			accounts_row_2 = {
					"account":company_business_trip_budget_chargeable_account,
					"cost_center":company_default_cost_center,
					"department":detail_row.main_department,
					"credit_in_account_currency":employee_total_amount,
			}
			accounts.append(accounts_row_2)
		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)

		frappe.msgprint(_("Journal Entry {0} is created").format(get_link_to_form("Journal Entry",je.name)),alert=1)
		