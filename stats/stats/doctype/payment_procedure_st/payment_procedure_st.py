# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,today
from stats.api import create_payment_journal_entry_from_payment_procedure


class PaymentProcedureST(Document):

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
		if not self.payment_type:
			frappe.throw(_("Please select payment type"))
		
		total_employee_amount = 0
		for row in self.employees:
			total_employee_amount = total_employee_amount + (row.amount or 0)

		company = erpnext.get_default_company()
		if self.payment_request_reference:
			company_default_central_bank_account = frappe.db.get_value("Company",company,"custom_default_central_bank_account")
			company_default_payment_order_account = frappe.db.get_value("Company",company,"custom_default_payment_order_account")
			company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
			

			if self.bank_enhancement_date:
				je_date = self.bank_enhancement_date
			else :
				je_date = today()
			create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_debit_account_mof,total_employee_amount,je_date)

			reference_type = frappe.db.get_value("Payment Request ST",self.payment_request_reference,"reference_name")
			if reference_type == "Business Trip Sheet ST":
				company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=today())
					create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())

				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())

			elif reference_type == "Employee Reallocation Sheet ST":
				company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=today())
					create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())
	
	# def create_payment_journal_entry_from_payment_procedure(name,debit_account,credit_account,amount,je_date=None):
	# 	if je_date == None:
	# 		je_date = today()

	# 	payment_je_doc = frappe.new_doc("Journal Entry")
	# 	payment_je_doc.voucher_type = "Journal Entry"
	# 	payment_je_doc.posting_date = je_date
	# 	payment_je_doc.custom_payment_procedure_reference = name

	# 	accounts = []

	# 	company = erpnext.get_default_company()
	# 	company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")

	# 	accounts_row = {
	# 		"account":debit_account,
	# 		"cost_center":company_default_cost_center,
	# 		"debit_in_account_currency":amount,
	# 	}
	# 	accounts.append(accounts_row)
	# 	accounts_row_2 = {
	# 		"account":credit_account,
	# 		"cost_center":company_default_cost_center,
	# 		"credit_in_account_currency":amount,
	# 	}
	# 	accounts.append(accounts_row_2)

	# 	payment_je_doc.set("accounts",accounts)
	# 	payment_je_doc.run_method('set_missing_values')
	# 	payment_je_doc.save(ignore_permissions=True)
	# 	payment_je_doc.submit()

	# 	frappe.msgprint(_("Payment Journal Entry is created from Payment Procedure {0}").format(get_link_to_form("Journal Entry",payment_je_doc.name)),alert=1)