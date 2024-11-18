# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_to_date

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
				frappe.throw(_("Please Set Notice Period Days in Employee Doctype."))
			elif test_period > getdate(self.last_working_days): 
				frappe.msgprint(_("Employee is in test period"), alert=1)
			else:
				today = getdate(nowdate())
				notice_period_end_date = add_to_date(today, days=notice_period_days)
				print(notice_period_end_date, "====", notice_period_days)
				if getdate(self.last_working_days) <= getdate(notice_period_end_date):
					frappe.throw(_("Last Working Day must be after Notice Period"))

	
	def set_relieving_date_in_employee(self):
		emp =  frappe.get_doc("Employee", self.employee_no)
		emp.relieving_date = self.last_working_days
		emp.save(ignore_permissions=True)
		frappe.msgprint(_("In {0} Employee Relieving Date Set to {1}").format(self.employee_no, self.last_working_days))
