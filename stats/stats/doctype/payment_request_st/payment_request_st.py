# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form,today
from frappe.model.document import Document


class PaymentRequestST(Document):

	def validate(self):
		total_amount = 0
		if len(self.employees)>0:
			for row in self.employees:
				total_amount = total_amount + (row.amount or 0)
		self.total_amount = total_amount
	def on_submit(self):
		company = erpnext.get_default_company()
		if self.reference_name == "Business Trip Sheet ST":
			company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_business_trip_budget_expense_account,company_business_trip_budget_chargeable_account)
			self.create_payment_procedure_on_submit_of_payment_request()
		elif self.reference_name == "Employee Reallocation Sheet ST":
			company_reallocation_budget_expense_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_expense_account")
			company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_reallocation_budget_expense_account,company_reallocation_budget_chargeable_account)
			self.create_payment_procedure_on_submit_of_payment_request()
	
	
	def create_journal_entry_on_submit_of_payment_request(self,company_budget_expense_account,company_budget_chargeable_account):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = today()
		je.custom_payment_request_reference = self.name
		
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
		""",self.name,as_dict=1,debug=1)
		print(employee_detais,"employee_detais")

		employee_total_amount = 0
		company = erpnext.get_default_company()
		if len(employee_detais)>0:
			# company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			# company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
			for detail_row in employee_detais:
				employee_total_amount = employee_total_amount + detail_row.amount
				department_cost_center = frappe.db.get_value("Department",detail_row.main_department,"custom_department_cost_center")
				accounts_row = {
					"account":company_budget_expense_account,
					"cost_center":department_cost_center,
					"department":detail_row.main_department,
					"debit_in_account_currency":detail_row.amount,
				}
				accounts.append(accounts_row)

			accounts_row_2 = {
					"account":company_budget_chargeable_account,
					"cost_center":company_default_cost_center,
					"department":detail_row.main_department,
					"credit_in_account_currency":employee_total_amount,
			}
			accounts.append(accounts_row_2)
		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)

	def create_payment_procedure_on_submit_of_payment_request(self):
		pp_doc = frappe.new_doc("Payment Procedure ST")
		pp_doc.payment_request_reference = self.name
		pp_doc.mode_of_payment = self.mode_of_payment
		pp_doc.mode_of_payment_type = self.payment_type
		pp_doc.budget_account = self.budget_account

		if len(self.employees)>0:
			for row in self.employees:
				pp_row = pp_doc.append("employees",{})
				pp_row.employee_no = row.employee_no
				pp_row.amount = row.amount

		pp_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Procedure {0} is created").format(get_link_to_form("Payment Procedure ST", pp_doc.name)),alert=1)