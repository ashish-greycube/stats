# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import today, get_link_to_form
from frappe.model.document import Document


class PettyCashRequestST(Document):

	def validate(self):
		self.set_total_loan_amount()
	def on_submit(self):
		self.create_payment_request_on_submit_of_pc_request()

	def set_total_loan_amount(self):
		total_loan_amount = 0
		if len(self.pc_request_account_details)>0:
			for row in self.pc_request_account_details:
				total_loan_amount = total_loan_amount + row.amount
		
		self.total_loan_amount = total_loan_amount

	def create_payment_request_on_submit_of_pc_request(self):

		company = erpnext.get_default_company()
		company_default_employee_petty_cash_account = frappe.db.get_value("Company",company,"custom_default_employee_petty_cash_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Petty Cash Request ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_employee_petty_cash_account
		pr_doc.party_type = "Employee"
		
		total_amount = 0
		if self.employee_no:
			pr_row = pr_doc.append("employees",{})
			pr_row.employee_no = self.employee_no
			if len(self.pc_request_account_details)>0:
				for row in self.pc_request_account_details:
					total_amount = total_amount + row.amount
			pr_row.amount = total_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	@frappe.whitelist()
	def create_petty_cash_closing(self):
		pc_closing_doc = frappe.new_doc("Petty Cash Closing ST")
		pc_closing_doc.petty_cash_request_reference = self.name
		
		if len(self.pc_request_account_details)>0:
			for row in self.pc_request_account_details:
				pc_closing_row = pc_closing_doc.append("pc_closing_account_details",{})
				pc_closing_row.account_name = row.account_name
				pc_closing_row.amount = row.amount

		pc_closing_doc.run_method('set_missing_values')
		pc_closing_doc.save(ignore_permissions=True)
		return pc_closing_doc.name