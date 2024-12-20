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
			
		if not self.total_amount:
			self.total_amount = total_amount

		self.set_party_name_based_on_party_type()

	def set_party_name_based_on_party_type(self):
		if self.party_type and self.party_type == "Employee":
			self.party_name_employee = "Multiple Payment"

	def on_submit(self):
		if not self.payment_type:
			frappe.throw(_("Please select payment type"))

		if self.reference_name in ["End Of Service Sheet ST","Vacation Encashment Sheet ST"]:
			if self.payment_type == "Indirect":
				frappe.throw(_("You cannot select payment type Indirect"))
		
		total_employee_amount = 0
		for row in self.employees:
			total_employee_amount = total_employee_amount + (row.amount or 0)

		company = erpnext.get_default_company()
		if self.payment_request_reference:
			company_default_central_bank_account = frappe.db.get_value("Company",company,"custom_default_central_bank_account")
			company_default_payment_order_account = frappe.db.get_value("Company",company,"custom_default_payment_order_account")
			company_default_debit_account_mof = frappe.db.get_value("Company",company,"custom_default_debit_account_mof")
			

			if self.payment_type == "Indirect":
				je_date = self.bank_enhancement_date
			else :
				je_date = self.transaction_date
			
			if self.reference_name not in ["End Of Service Sheet ST","Vacation Encashment Sheet ST"]:
				create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_debit_account_mof,self.total_amount,je_date)

			if self.reference_name == "Business Trip Sheet ST":
				company_business_trip_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())

				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_business_trip_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())

			elif self.reference_name == "Employee Reallocation Sheet ST":
				company_reallocation_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_reallocation_budget_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_reallocation_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())
			
			elif self.reference_name == "Overtime Sheet ST":
				company_overtime_budget_chargeable_account = frappe.db.get_value("Company",company,"custom_overtime_budget_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_overtime_budget_chargeable_account,company_default_central_bank_account,total_employee_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_overtime_budget_chargeable_account,self.middle_bank_account,total_employee_amount,je_date=today())

			elif self.reference_name == "Petty Cash Request ST":
				company_default_employee_petty_cash_account = frappe.db.get_value("Company",company,"custom_default_employee_petty_cash_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.transaction_date)
					if len(self.employees)>0:
						for row in self.employees:
							create_payment_journal_entry_from_payment_procedure(self,company_default_employee_petty_cash_account,company_default_central_bank_account,total_employee_amount,je_date=today(),party_type=self.party_type,party_name=row.employee_no)
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,total_employee_amount,je_date=self.bank_enhancement_date)
						if len(self.employees)>0:
							for row in self.employees:
								create_payment_journal_entry_from_payment_procedure(self,company_default_employee_petty_cash_account,self.middle_bank_account,total_employee_amount,je_date=today(),party_type=self.party_type,party_name=row.employee_no)
				pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.reference_no)
				pc_request_doc.payment_status = "Paid"
				pc_request_doc.add_comment("Comment", text="Payment Status changed to Paid due to {0}".format(get_link_to_form("Payment Procedure ST",self.name)))
				pc_request_doc.save(ignore_permissions=True)
				frappe.msgprint(_("PC Request {0} payment status changed to <b>Paid</b>".format(get_link_to_form("Petty Cash Request ST",self.reference_no))),alert=True)
				
			elif self.reference_name == "Achievement Certificate ST":
				company_default_international_subscription_chargeable_account = frappe.db.get_value("Company",company,"custom_default_international_subscription_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_default_international_subscription_chargeable_account,company_default_central_bank_account,self.total_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_default_international_subscription_chargeable_account,self.middle_bank_account,self.total_amount,je_date=today())

			elif self.reference_name == "Employee Annual Reward ST":
				company_annual_reward_chargeable_account = frappe.db.get_value("Company",company,"custom_annual_reward_chargeable_account")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_annual_reward_chargeable_account,company_default_central_bank_account,self.total_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_annual_reward_chargeable_account,self.middle_bank_account,self.total_amount,je_date=today())
			
			elif self.reference_name == "End Of Service Sheet ST":
				create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_debit_account_mof,self.total_amount,je_date=self.transaction_date)
				create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_central_bank_account,self.total_amount,je_date=today())
			
			elif self.reference_name == "Vacation Encashment Sheet ST":
				create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_debit_account_mof,self.total_amount,je_date=self.transaction_date)
				create_payment_journal_entry_from_payment_procedure(self,company_default_payment_order_account,company_default_central_bank_account,self.total_amount,je_date=today())
			
			elif self.reference_name == "Education Allowance Sheet ST":
				company_education_allowance_chargeable_account_ = frappe.db.get_value("Company",company,"custom_education_allowance_chargeable_account_")
				if self.payment_type == "Direct":
					create_payment_journal_entry_from_payment_procedure(self,company_default_central_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.transaction_date)
					create_payment_journal_entry_from_payment_procedure(self,company_education_allowance_chargeable_account_,company_default_central_bank_account,self.total_amount,je_date=today())
				elif self.payment_type == "Indirect":
					if self.middle_bank_account:
						create_payment_journal_entry_from_payment_procedure(self,self.middle_bank_account,company_default_payment_order_account,self.total_amount,je_date=self.bank_enhancement_date)
						create_payment_journal_entry_from_payment_procedure(self,company_education_allowance_chargeable_account_,self.middle_bank_account,self.total_amount,je_date=today())