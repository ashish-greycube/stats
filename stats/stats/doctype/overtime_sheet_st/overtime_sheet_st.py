# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff
from stats.stats.report.employee_attendance.employee_attendance import execute
from stats.hr_utils import get_latest_total_monthly_salary_of_employee


class OvertimeSheetST(Document):
	
	def validate(self):
		self.calculate_amount_based_on_actual_extra_hours_and_set_total_amount()
	
	def on_submit(self):
		self.create_payment_request_on_submit_of_ot_sheet()

	def calculate_amount_based_on_actual_extra_hours_and_set_total_amount(self):
		if len(self.overtime_sheet_employee_details)>0:
			total_amount = 0
			for row in self.overtime_sheet_employee_details:
				if row.actual_extra_hours > 0:
					monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
					per_day_salary = ((monthly_salary or 0)/30)
					amount = row.actual_extra_hours * per_day_salary
					row.amount = amount
					total_amount = total_amount + amount

			self.total_amount = total_amount

	def create_payment_request_on_submit_of_ot_sheet(self):
		pass
	
	@frappe.whitelist()
	def fetch_employees_from_overtime_request(self):
		final_overtime_employee_list = []
		filters = {"docstatus":1,"overtime_start_date":["between",[self.from_date,self.to_date]],"overtime_end_date":["between",[self.from_date,self.to_date]]}

		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department

		overtime_employee_list = frappe.db.get_all("Overtime Request ST",
											 filters=filters,
											 fields=["name"])
		if len(overtime_employee_list)>0:
			for overtime in overtime_employee_list:
				print(overtime_employee_list,"overtime_employee_list ==============")
				overtime_request_doc = frappe.get_doc("Overtime Request ST",overtime.name)
				if len(overtime_request_doc.employee_overtime_request)>0:
					overtime_days = date_diff(overtime_request_doc.overtime_end_date,overtime_request_doc.overtime_start_date) + 1
					for row in overtime_request_doc.employee_overtime_request:
						overtime_employee_details = {}
						print(overtime_request_doc.name,"---------- overtime_request_doc ---------------")
						overtime_employee_details["employee_no"]=row.employee_no
						overtime_employee_details["requested_date"]=overtime_request_doc.creation_date
						overtime_employee_details["overtime_request_reference"]=overtime_request_doc.name
						required_extra_hours = row.no_of_hours_per_day * overtime_days
						overtime_employee_details["required_extra_hours"]=required_extra_hours

						filters_for_report = frappe._dict({"employee":row.employee_no,"from_date":overtime_request_doc.overtime_start_date,"to_date":overtime_request_doc.overtime_end_date})
						print(filters_for_report,"filters_for_report +++++++++++++++++++")
						data_from_report = execute(filters_for_report)
						print(data_from_report[1],"-----------------------------------")
						total_actual_extra_hours = 0
						for record in data_from_report[1]:
							if record.extra_hours:
								total_actual_extra_hours = total_actual_extra_hours + record.extra_hours
						overtime_employee_details["actual_extra_hours"]=total_actual_extra_hours
						monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
						print(monthly_salary,"*  "*10)
						amount = (total_actual_extra_hours or 0) * (row.overtime_rate_per_hour or 0)
						overtime_employee_details["amount"]=amount
						overtime_employee_details["overtime_rate_per_hour"]=row.overtime_rate_per_hour

						final_overtime_employee_list.append(overtime_employee_details)

		print(final_overtime_employee_list,"+   "*10)
		return final_overtime_employee_list

