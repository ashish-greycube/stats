# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from stats.hr_utils import (check_if_holiday_between_applied_dates, 
							check_employee_in_scholarship, check_employee_in_training, 
							check_available_amount_for_budget,
							get_latest_total_monthly_salary_of_employee)
from frappe.utils import date_diff, flt

class OvertimeRequestST(Document):
	def validate(self):
		self.validate_overtime_dates()
		self.calculate_employee_due_amount()
		# self.validate_budget_for_overtime()

	def on_submit(self):
		self.validate_budget_for_overtime()

	def validate_overtime_dates(self):
		if self.overtime_start_date and self.overtime_end_date and self.overtime_start_date > self.overtime_end_date:
			frappe.throw(_("Overtime start date cann't be greater than overtime end date"))

	def calculate_employee_due_amount(self):
		if len(self.employee_overtime_request) > 0:
			total_due_amt = 0
			no_of_day = date_diff(self.overtime_end_date, self.overtime_start_date)
			for row in self.employee_overtime_request:	
				monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
				row.due_amount = (row.no_of_hours_per_day or 0) * (no_of_day or 0) * ((monthly_salary or 0)/30)
				row.rate_per_hour = ((monthly_salary or 0)/(30 * 8)) 
				row.overtime_rate_per_hour = (row.rate_per_hour * 0.5) + row.rate_per_hour
				total_due_amt = total_due_amt + (row.due_amount or 0)
				print(row.due_amount, '---row.due_amount')

			self.total_due_amount = total_due_amt

	def validate_budget_for_overtime(self):
		if self.total_due_amount:
			company = erpnext.get_default_company()
			budget_account = frappe.db.get_value("Company", company, "custom_overtime_budget_expense_account")
			cost_center = frappe.db.get_value("Department", self.main_department, "custom_department_cost_center")

			budget = check_available_amount_for_budget(budget_account,cost_center)
			print(budget, '--busget')
			if self.total_due_amount > budget:
				frappe.throw(_("Total Due amount {0} can't be greater than Budget Amount: {1}").format(self.total_due_amount, budget))

	@frappe.whitelist()
	def get_employee(self):
		emp = {}
		emp_list=[]
		employee_list = frappe.db.get_all("Employee", filters={"status":"Active", "department":self.main_department}, fields=["name"])
		if len(employee_list) > 0:
			for employee in employee_list:
				scholarship = check_employee_in_scholarship(employee.name,self.overtime_start_date, self.overtime_end_date)
				training = check_employee_in_training(employee.name,self.overtime_start_date, self.overtime_end_date)
				holiday = check_if_holiday_between_applied_dates(employee.name, self.overtime_start_date, self.overtime_end_date)
				# print(scholarship, '--scholarship', training, '--training', holiday, '--holiday', employee.name)
				if scholarship == True:
					print(employee.name, '==scholarship')
					frappe.msgprint(_("Employee {0} is applied for scholarship").format(employee.name), alert=1)
					continue
				if training == True:
					print(employee.name, '==training')
					frappe.msgprint(_("Employee {0} is in training").format(employee.name), alert=1)
					continue
				print(holiday, flt(date_diff(self.overtime_end_date, self.overtime_start_date) + 1), '==================')
				# if holiday !=  flt(date_diff(self.overtime_end_date, self.overtime_start_date)):
				if holiday == True:
					print(employee.name, '==holiday')
					frappe.msgprint(_("Employee {0} has holiday during overtime request dates").format(employee.name), alert=1)
					continue

				emp["employee_no"]=employee.name
				emp_list.append(emp.copy())
					# print(emp, '--for dict')

		print(emp, '---dict')
		return emp_list