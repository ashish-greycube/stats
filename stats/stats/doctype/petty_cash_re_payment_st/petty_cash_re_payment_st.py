# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class PettyCashRePaymentST(Document):
	
	def on_submit(self):
		self.validate_attachment()
		self.create_jv_for_repayment()
	
	def validate_attachment(self):
		if not self.payment_proof_attachment:
			frappe.throw(_("Please attach payment proof"))

	def create_jv_for_repayment(self):
		pc_request_doc = frappe.get_doc("Petty Cash Request ST",self.petty_cash_request_reference)
		department_cost_center = frappe.db.get_value("Department",pc_request_doc.main_department,"custom_department_cost_center")

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.creation_date
		# je.custom_petty_cash_repayment_reference = self.name
		
		accounts = []
		company = erpnext.get_default_company()
		company_default_cost_center = frappe.db.get_value("Company",company,"cost_center")
		company_default_bank_account = frappe.db.get_value("Company",company,"default_bank_account")
		
		accounts_row = {
			"account":company_default_bank_account,
			"cost_center":company_default_cost_center,
			"debit_in_account_currency":self.total_unpaid,
		}
		accounts.append(accounts_row)

		if len(self.pc_repayment_account_details)>0:
			for row in self.pc_repayment_account_details:
				accounts_row_2 = {
						"account":row.account_name,
						"cost_center":department_cost_center,
						"credit_in_account_currency":row.unpaid_amount
				}
				accounts.append(accounts_row_2)

		je.set("accounts",accounts)
		je.run_method('set_missing_values')
		je.save(ignore_permissions=True)
		je.submit()
		frappe.msgprint(_("Journal Entry is created {0}").format(get_link_to_form("Journal Entry",je.name)),alert=1)

	@frappe.whitelist()
	def create_deposit_to_mof(self):
		pass