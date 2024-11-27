# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import month_diff, today, getdate, add_to_date
from frappe.model.document import Document


class EmployeeAlternativesST(Document):
	
	@frappe.whitelist()
	def fetch_employees_based_on_filters(self):
		all_active_employee_list = frappe.db.get_all("Employee",
											   filters={"status":"Active"},
											   fields=["name","date_of_retirement","date_of_joining"])
		
		experienced_and_non_retired_employees = []
		if len(all_active_employee_list)>0:
			for employee in all_active_employee_list:
				employee_years_of_retirement = month_diff(employee.date_of_retirement, today())/12
				print(employee_years_of_retirement,"employee_years_of_retirement",type(employee_years_of_retirement),employee.name)
				if employee_years_of_retirement > self.no_of_years_for_retirement:
					employee_years_of_experience = month_diff(today(), employee.date_of_joining)/12
					print(employee_years_of_experience,"---------------employee_years_of_experience",type(employee_years_of_experience))
					if employee_years_of_experience > self.no_of_years_of_experience:
						employee_qualification = frappe.db.get_value("Employee Education",{"parent":employee.name},"level")
						print(employee_qualification,"==============employee_qualification")
						if employee_qualification and employee_qualification == self.qualification:
							experienced_and_non_retired_employees.append(employee.name)
		
		current_year = getdate(today()).year
		previous_year = getdate(add_to_date(today(), years=-1)).year

		employee_eveluation_list = frappe.db.get_all("Employee Evaluation ST",
											   filters={"evaluation_type":self.evaluation_type},
											   fields=["name","evaluation_classification","evaluation_from","evaluation_to"])
		if len(employee_eveluation_list)>0:
			for evaluation in employee_eveluation_list:
				pass
		print(current_year,"-----current_year",previous_year,"-----previous_year")