# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class PettyCashClosingST(Document):
	
	def validate(self):
		self.calculate_paid_unpaid_amount()

	def on_submit(self):
		self.validate_paid_amount()
		self.change_status_of_pc_request()

	def calculate_paid_unpaid_amount(self):
		total_loan_amount = 0
		total_paid_amount = 0
		total_unpaid_amount = 0
		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				total_loan_amount = total_loan_amount + row.amount
				total_paid_amount = total_paid_amount + row.paid_amount
				row.unpaid_amount = row.amount - row.paid_amount
				total_unpaid_amount = total_unpaid_amount + row.unpaid_amount

		self.total_loan_amount = total_loan_amount
		self.total_paid_amount = total_paid_amount
		self.total_unpaid_amount = total_unpaid_amount

	def validate_paid_amount(self):
		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				if not row.paid_amount:
					frappe.throw(_("#Row {0}: Please fill paid amount".format(row.idx)))

	def change_status_of_pc_request(self):
		if self.petty_cash_request_reference:
			pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.petty_cash_request_reference)
			pc_request_doc.loan_status = "Closed"
			pc_request_doc.add_comment("Comment",text = "Loan Status changed to Closed due to {0}".format(get_link_to_form("Petty Cash Closing ST",self.name)))
			pc_request_doc.save(ignore_permissions=True)
			frappe.msgprint(_("PC Request {0} Loan status changed to <b>Closed</b>".format(get_link_to_form("Petty Cash Request ST",self.petty_cash_request_reference))),alert=True)
	
	@frappe.whitelist()
	def create_petty_cash_repayment(self):
		pc_repayment_doc = frappe.new_doc("Petty Cash Re-Payment ST")
		pc_repayment_doc.petty_cash_closing_reference = self.name
		pc_repayment_doc.petty_cash_request_reference = self.petty_cash_request_reference
		pc_repayment_doc.deposit_amount = self.total_unpaid_amount
		pc_repayment_doc.total_unpaid = self.total_unpaid_amount

		if len(self.pc_closing_account_details)>0:
			for row in self.pc_closing_account_details:
				pc_repayment_row = pc_repayment_doc.append("pc_repayment_account_details", {})
				pc_repayment_row.account_name = row.account_name
				pc_repayment_row.amount = row.amount
				pc_repayment_row.paid_amount = row.paid_amount
				pc_repayment_row.unpaid_amount = row.unpaid_amount
			
		pc_repayment_doc.run_method('set_missing_values')
		pc_repayment_doc.save(ignore_permissions = True)
		return pc_repayment_doc.name