# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import month_diff,today


class HighPerformanceEmployeeST(Document):
	pass
	@frappe.whitelist()
	def fetch_employees_from_employee_evaluation(self):
		filters = {"evaluation_classification":["in",[ele.evaluation_classification for ele in self.employee_evaluation]],"docstatus":1}
		
		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department

		print(filters,"-----------------------------------------------------")
		
		final_employee_list = []
		employee_from_employee_evaluation = frappe.db.get_all("Employee Evaluation ST",
														filters=filters,
														fields=["name","employee_no","final_evaluation","evaluation_classification"])
		print(employee_from_employee_evaluation,"employee_from_employee_evaluation----")
		if len(employee_from_employee_evaluation)>0:
			for employee in employee_from_employee_evaluation:
				employee_retirement_date = frappe.db.get_value("Employee",employee.employee_no,"date_of_retirement")
				if employee_retirement_date:
					print(employee_retirement_date,"employee_retirement_date",type(employee_retirement_date))
					employee_years_of_retirement = month_diff(employee_retirement_date, today())/12
					print(employee_years_of_retirement,"employee_years_of_retirement",type(employee_years_of_retirement))
					if employee_years_of_retirement > self.no_of_years_for_retirement:
						final_employee_list.append(employee)

		return final_employee_list