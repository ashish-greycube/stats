# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from stats.api import fetch_employee_per_diem_amount
from frappe.utils import today


class BusinessTripSheetST(Document):
	def validate(self):
		self.calculate_approved_amount()
		self.set_ticket_amount_and_total_amount()
		self.validate_start_date_and_end_date()

	def calculate_approved_amount(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				employee_no = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"employee_no")
				approved_amount = fetch_employee_per_diem_amount(employee_no,row.approved_days)
				print(approved_amount,"approved_amount")
				row.approved_amount = approved_amount
	
	def set_ticket_amount_and_total_amount(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				ticket_request_name = frappe.db.get_all("Ticket Request ST",filters={"business_trip_reference":row.business_trip_reference},fields=["name"])
				if len(ticket_request_name)>0:
					ticket_value = frappe.db.get_value("Ticket Request ST",ticket_request_name[0].name,"ticket_value")
					row.ticket_amount = ticket_value
				row.total_amount = (row.ticket_amount or 0) + (row.approved_amount or 0)

	def validate_start_date_and_end_date(self):
		if self.from_date and self.to_date:
			if self.to_date < self.from_date:
				frappe.throw(_("End date can not be less than Start date"))

	def on_submit(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				frappe.db.set_value("Employee Task Completion ST",row.employee_task_completion_reference,"process_status","Processed")
				frappe.msgprint(_("Process status of {0} is changed to {1}").format(get_link_to_form("Employee Task Completion ST", row.employee_task_completion_reference),"Processed"),alert=1)
				ticket_request_name = frappe.db.get_all("Ticket Request ST",filters={"business_trip_reference":row.business_trip_reference},fields=["name"])
				if len(ticket_request_name)>0:
					frappe.db.set_value("Ticket Request ST",ticket_request_name[0].name,"process_status","Processed")
					frappe.msgprint(_("Process status of {0} is changed to {1}").format(get_link_to_form("Ticket Request ST", ticket_request_name[0].name),"Processed"),alert=1)
				
			self.create_payment_request_on_submit_of_bts()

	def create_payment_request_on_submit_of_bts(self):
		company = erpnext.get_default_company()
		company_default_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Business Trip Sheet ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_business_trip_budget_expense_account
		
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.total_amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	@frappe.whitelist()
	def get_business_trip(self):
		if not self.from_date:
			frappe.throw(_("From date is requied"))
		if not self.to_date:
			frappe.throw(_("To date is requied"))

		filters={"docstatus":1,"process_status": "Pending","task_creation_date":["between", [self.from_date, self.to_date]]}
		# if self.main_department:
		# 	filters["main_department"]=self.main_department
		# if self.sub_department:
		# 	filters["sub_department"]=self.sub_department
		etc = frappe.db.get_all('Employee Task Completion ST', filters=filters,fields=["name"])
		print(etc, '--------etc')
		return etc