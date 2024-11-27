# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff,today,get_link_to_form
from stats.stats.report.employee_attendance.employee_attendance import execute
from stats.hr_utils import get_latest_total_monthly_salary_of_employee


class OvertimeSheetST(Document):
	
	def validate(self):
		self.calculate_amount_based_on_actual_extra_hours_and_set_total_amount()
		self.validate_start_date_and_end_date()
		# self.create_payment_request_on_submit_of_ot_sheet()
	
	def on_submit(self):
		self.create_payment_request_on_submit_of_ot_sheet()

	def calculate_amount_based_on_actual_extra_hours_and_set_total_amount(self):
		if len(self.overtime_sheet_employee_details)>0:
			total_amount = 0
			for row in self.overtime_sheet_employee_details:
				if row.actual_extra_hours > 0:
					amount = row.actual_extra_hours * row.overtime_rate_per_hour
					row.amount = amount
					total_amount = total_amount + amount

			self.total_amount = total_amount
	
	def validate_start_date_and_end_date(self):
		if self.from_date and self.to_date:
			if self.to_date < self.from_date:
				frappe.throw(_("End date can not be less than Start date"))

	def create_payment_request_on_submit_of_ot_sheet(self):

		company = erpnext.get_default_company()
		company_default_overtime_budget_expense_account = frappe.db.get_value("Company",company,"custom_overtime_budget_expense_account")
		pr_doc = frappe.new_doc("Payment Request ST")
		pr_doc.date = today()
		pr_doc.reference_name = "Overtime Sheet ST"
		pr_doc.reference_no = self.name
		pr_doc.budget_account = company_default_overtime_budget_expense_account
		pr_doc.party_type = "Employee"
		
		if len(self.overtime_sheet_employee_details)>0:
			for row in self.overtime_sheet_employee_details:
				pr_row = pr_doc.append("employees",{})
				pr_row.employee_no = row.employee_no
				pr_row.amount = row.amount

		pr_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Payment Request {0} is created").format(get_link_to_form("Payment Request ST", pr_doc.name)),alert=1)

	@frappe.whitelist()
	def fetch_employees_from_overtime_request(self):
		final_overtime_employee_list = []
		filters = {"docstatus":1,"status":"Approved","overtime_start_date":["between",[self.from_date,self.to_date]],"overtime_end_date":["between",[self.from_date,self.to_date]]}

		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department

		overtime_employee_list = frappe.db.get_all("Overtime Request ST",
											 filters=filters,
											 fields=["name"])

		overtime_sheet_list = frappe.db.get_all("Overtime Sheet Employee Details ST",fields=["overtime_request_reference"])
		final_overtime_request_list = []
		for overtime_request in overtime_employee_list:
			found=False
			if len(overtime_sheet_list)>0:
				for ele in overtime_sheet_list:
					if ele.overtime_request_reference == overtime_request.name:
						found=True
						break
			if found==False:
				final_overtime_request_list.append(overtime_request)

		if len(final_overtime_request_list)>0:
			for overtime in final_overtime_request_list:
				print(final_overtime_request_list,"final_overtime_request_list ==============")
				overtime_request_doc = frappe.get_doc("Overtime Request ST",overtime.name)
				if len(overtime_request_doc.employee_overtime_request)>0:
					overtime_days = date_diff(overtime_request_doc.overtime_end_date,overtime_request_doc.overtime_start_date) + 1
					for row in overtime_request_doc.employee_overtime_request:
						overtime_employee_details = {}
						print(overtime_request_doc.name,"---------- overtime_request_doc ---------------")
						overtime_employee_details["employee_no"]=row.employee_no
						overtime_employee_details["employee_name"]=row.employee_name
						overtime_employee_details["requested_date"]=overtime_request_doc.creation_date
						overtime_employee_details["overtime_request_reference"]=overtime_request_doc.name
						required_extra_hours = row.no_of_hours_per_day * overtime_days
						overtime_employee_details["required_extra_hours"]=required_extra_hours

						filters_for_report = frappe._dict({"employee":row.employee_no,"from_date":overtime_request_doc.overtime_start_date,"to_date":overtime_request_doc.overtime_end_date})
						print(filters_for_report,"filters_for_report +++++++++++++++++++")
						data_from_report = execute(filters_for_report)
						print(data_from_report[1],"-----------------------------------")
						total_actual_extra_mins = 0
						for record in data_from_report[1]:
							if record.extra_minutes and record.extra_minutes >= 0:
								print(record.extra_minutes,"=============record.extra_minutes")
								total_actual_extra_mins = total_actual_extra_mins + record.extra_minutes
						total_actual_extra_hours = total_actual_extra_mins / 60
						overtime_employee_details["actual_extra_hours"]=total_actual_extra_hours
						amount = (total_actual_extra_hours or 0) * (row.overtime_rate_per_hour or 0)
						overtime_employee_details["amount"]=amount
						overtime_employee_details["overtime_rate_per_hour"]=row.overtime_rate_per_hour

						final_overtime_employee_list.append(overtime_employee_details)

		print(final_overtime_employee_list,"+   "*10)
		return final_overtime_employee_list

