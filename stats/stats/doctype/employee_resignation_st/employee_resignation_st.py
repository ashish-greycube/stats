# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_to_date
from stats.salary import get_latest_salary_structure_assignment

class EmployeeResignationST(Document):
	def validate(self):
		self.validate_resignation_date()

	def on_submit(self):
		self.set_relieving_date_in_employee()

	def validate_resignation_date(self):
		if self.last_working_days:
			today_month = getdate(nowdate()).month
			resignation_month = getdate(self.last_working_days).month

			if today_month == resignation_month:
				# today_date = nowdate().day
				last_working_days = getdate(self.last_working_days).day

				if last_working_days >= 11:
					frappe.throw(_("For this Month, Payroll is generated so you cann't apply for resignation"))

			# Last Working day should not be less than notic period
			notice_period_days = frappe.db.get_value("Employee", self.employee_no, 'notice_number_of_days')
			joining_date = frappe.db.get_value("Employee", self.employee_no, 'date_of_joining')
			test_period = add_to_date(getdate(joining_date), months=6)

			if not notice_period_days:
				frappe.throw(_("Please Set Notice Period Days in Employee Profile."))
			elif test_period > getdate(self.last_working_days): 
				frappe.msgprint(_("Employee is in test period"), alert=1)
			else:
				today = getdate(nowdate())
				notice_period_end_date = add_to_date(today, days=notice_period_days)
				print(notice_period_end_date, "====", notice_period_days)
				if getdate(self.last_working_days) <= getdate(notice_period_end_date):
					frappe.throw(_("Last Working Day must be after Notice Period"))

			if self.resignation_type == "Not Renew-Contract":
				resignation_date = self.last_working_days
				resignation_to_be_allow_date = add_to_date(getdate(resignation_date), days=notice_period_days)
				employee_contract_end_date = frappe.db.get_value("Employee", self.employee_no, 'contract_end_date')
				print(resignation_to_be_allow_date,"resignation_to_be_allow_date")
				if resignation_to_be_allow_date < getdate(employee_contract_end_date):
					print(resignation_to_be_allow_date, getdate(employee_contract_end_date))
					frappe.throw(_("You cannot resign before {0}".format(employee_contract_end_date)))
	
	def set_relieving_date_in_employee(self):
		emp =  frappe.get_doc("Employee", self.employee_no)
		emp.relieving_date = self.last_working_days
		emp.save(ignore_permissions=True)
		frappe.msgprint(_("In {0} Employee Relieving Date Set to {1}").format(self.employee_no, self.last_working_days), alert=1)

	@frappe.whitelist()
	def create_end_of_service(self):
		eos = frappe.new_doc("End of Service Calculation ST")

		eos.resignation_reference = self.name
		eos.employee = self.employee_no
		eos.resignation_type = self.resignation_type
		eos.seperation_reason = self.separation_reason
		eos.end_of_service_type = "Resignation"

		eos.save(ignore_permissions=True)

		return eos.name
	
	@frappe.whitelist()
	def create_evacuation_of_party(self):
		eop = frappe.new_doc("Evacuation of Party ST")

		eop.resignation_reference = self.name
		eop.employee_no = self.employee_no
		eop.save(ignore_permissions=True)

		return eop.name
	
	@frappe.whitelist()
	def create_exit_interview(self):
		ei = frappe.new_doc("Exit Interview ST")
		ei.resignation_reference = self.name
		ei.employee_no = self.employee_no

		ei.save(ignore_permissions=True)

		return ei.name
				