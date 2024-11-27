# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import today, get_link_to_form
from frappe.model.document import Document


class EndOfServiceSheetST(Document):

	def on_submit(self):
		self.create_payment_request_on_submit_of_sheet()
	
	@frappe.whitelist()
	def get_employee_details_for_end_of_service(self):
		list_emp = frappe.db.get_all("End of Service Calculation ST", filters={"creation_date":["Between", [self.from_date, self.to_date]]},
							   fields=["name", "employee", "total_monthly_salary", "end_of_service_due_amount"])
		
		return list_emp

	def create_payment_request_on_submit_of_sheet(self):
		company = erpnext.get_default_company()
		custom_end_of_service_budget_expense_account = frappe.db.get_value("Company",company,"custom_overtime_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = self.doctype
		pr_doc.reference_no = self.name
		pr_doc.budget_account = custom_end_of_service_budget_expense_account
		pr_doc.party_type = "Employee"
		
		if len(self.employee_details)>0:
			for row in self.employee_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.due_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)