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
from frappe.utils import date_diff

class OvertimeRequestST(Document):
	def validate(self):
		self.calculate_employee_due_amount()
		self.validate_budget_for_overtime()

	def calculate_employee_due_amount(self):
		company = erpnext.get_default_company()
		if len(self.employee_overtime_request) > 0:
			total_due_amt = 0
			no_of_day = date_diff(self.overtime_end_date, self.overtime_start_date)
			for row in self.employee_overtime_request:	
				monthly_salary = get_latest_total_monthly_salary_of_employee(row.employee_no)
				# print(monthly_salary, type(monthly_salary))
				# print(row.employee_no, '--employee_no')
				row.due_amount = row.no_of_hours_per_day * no_of_day * ((monthly_salary or 0)/30)
				row.rate_per_hour = ((monthly_salary or 0)/(30 * 8)) 
				row.overtime_rate_per_hour = (row.rate_per_hour * 0.5) + row.rate_per_hour
				total_due_amt = total_due_amt + row.due_amount
				print(row.due_amount, '---row.due_amount')
				# print('-----------------------------------------------------------------------')


			budget_account = frappe.db.get_value("Company", company, "custom_overtime_budget_expense_account")
			cost_center = frappe.db.get_value("Department", self.main_department, "custom_department_cost_center")

			budget = check_available_amount_for_budget(budget_account,cost_center)
			print(budget, '--busget')
			if total_due_amt > budget:
				frappe.throw(_("Total of Due amount can't be grater than Budget Amount: {0}").format(budget))


	def validate_budget_for_overtime(self):
		if len(self.employee_overtime_request) > 0:
			pass

	@frappe.whitelist()
	def get_employee(self):
		emp = {}
		emp_list=[]
		
		employee_list = frappe.db.get_all("Employee", filters={"status":"Active"}, fields=["name"])
		if len(employee_list) > 0:
			for employee in employee_list:
				scholarship = check_employee_in_scholarship(employee.name,self.overtime_start_date, self.overtime_end_date)
				training = check_employee_in_training(employee.name,self.overtime_start_date, self.overtime_end_date)
				holiday = check_if_holiday_between_applied_dates(self.overtime_start_date, self.overtime_end_date,employee.name)
				if scholarship == None and training == None and holiday !=  date_diff(self.overtime_end_date, self.overtime_start_date):
					emp["employee_no"]=employee.name
					emp_list.append(emp.copy())
					# print(emp, '--for dict')

		print(emp, '---dict')
		return emp_list