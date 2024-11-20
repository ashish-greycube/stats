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

		self.set_party_name_based_on_party_type()

	def set_party_name_based_on_party_type(self):
		if self.party_type and self.party_type == "Employee":
			self.party_name_employee = "Multiple Payment"

	def on_submit(self):
		company = erpnext.get_default_company()
		self.create_payment_procedure_on_submit_of_payment_request()
		if self.reference_name == "Business Trip Sheet ST":
			company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_business_trip_budget_expense_account,company_business_trip_budget_chargeable_account)

		elif self.reference_name == "Employee Reallocation Sheet ST":
			company_reallocation_budget_expense_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_expense_account")
			company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_reallocation_budget_expense_account,company_reallocation_budget_chargeable_account)

		elif self.reference_name == "Overtime Sheet ST":
			company_overtime_budget_expense_account = frappe.db.get_value("Company",company,"custom_overtime_budget_expense_account")
			company_overtime_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_overtime_budget_chargeable_account")
			self.create_journal_entry_on_submit_of_payment_request(company_overtime_budget_expense_account,company_overtime_budget_chargeable_account)

	
	
	def create_journal_entry_on_submit_of_payment_request(self,company_budget_expense_account,company_budget_chargeable_account):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.transaction_date
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
		
		# Second JV from PR
		company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
		company_default_revenue_account = frappe.db.get_value("Company",company,"custom_default_revenue_account")

		payment_je_doc = frappe.new_doc("Journal Entry")
		payment_je_doc.voucher_type = "Journal Entry"
		payment_je_doc.posting_date = self.transaction_date
		payment_je_doc.custom_payment_request_reference = self.name

		jv_accounts = []

		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

		employee_info = frappe.db.sql("""
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
		print(employee_info,"employee_info")

		accounts_row = {
					"account":company_default_debit_account_mof,
					"cost_center":company_default_cost_center,
					"debit_in_account_currency":employee_total_amount,
				}
		jv_accounts.append(accounts_row)

		if len(employee_detais)>0:
			for row in employee_info:
				department_cost_center = frappe.db.get_value("Department",row.main_department,"custom_department_cost_center")
				accounts_row_2 = {
					"account":company_default_revenue_account,
					"cost_center":department_cost_center,
					"department":row.main_department,
					"credit_in_account_currency":row.amount,
				}
				jv_accounts.append(accounts_row_2)

		payment_je_doc.set("accounts",jv_accounts)
		payment_je_doc.run_method('set_missing_values')
		payment_je_doc.save(ignore_permissions=True)
		payment_je_doc.submit()

		frappe.msgprint(_("Journal Entry Due Expense is created from Payment Request {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)
		
	def create_payment_procedure_on_submit_of_payment_request(self):
		pp_doc = frappe.new_doc("Payment Procedure ST")
		pp_doc.payment_request_reference = self.name
		pp_doc.budget_account = self.budget_account
		pp_doc.party_type = self.party_type
		pp_doc.reference_name = self.reference_name
		pp_doc.reference_no = self.reference_no

		if len(self.employees)>0:
			for row in self.employees:
				pp_row = pp_doc.append("employees",{})
				pp_row.employee_no = row.employee_no
				pp_row.amount = row.amount

		pp_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Procedure {0} is created").format(get_link_to_form("Payment Procedure ST", pp_doc.name)),alert=1)