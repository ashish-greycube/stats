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
		
		# fetch employee based on experience and no of year of retirement
		experienced_and_non_retired_employees = []
		if len(all_active_employee_list)>0:
			for employee in all_active_employee_list:
				employee_years_of_retirement = month_diff(employee.date_of_retirement, today())/12
				if employee_years_of_retirement > self.no_of_years_for_retirement:
					employee_years_of_experience = month_diff(today(), employee.date_of_joining)/12
					if employee_years_of_experience > self.no_of_years_of_experience:
						employee_qualification = frappe.db.get_value("Employee Education",{"parent":employee.name},"level")
						if employee_qualification and employee_qualification == self.qualification:
							experienced_and_non_retired_employees.append(employee.name)
		
		current_year = getdate(today()).year
		previous_year = getdate(add_to_date(today(), years=-1)).year
		final_employee_list = []

		# fetch employee based on evaluation classification
		for emp in experienced_and_non_retired_employees:
			previous_evaluation = False
			current_evaluation = False
			employee_eveluation_list = frappe.db.get_all("Employee Evaluation ST",
											filters={"evaluation_type":self.evaluation_type,"employee_no":emp,"docstatus":1},
											fields=["name","evaluation_classification","evaluation_from","evaluation_to","employee_no","employee_name"])
			emp_details = {}
			if len(employee_eveluation_list)>0:
				for evaluation in employee_eveluation_list:
					if (evaluation.evaluation_from).year == previous_year and (evaluation.evaluation_to).year == previous_year:
						if evaluation.evaluation_classification in [ele.evaluation_classification for ele in self.previous_year_evaluation]:
							previous_evaluation = True
							emp_details["previous_year_evaluation"] = evaluation.evaluation_classification
							
					elif (evaluation.evaluation_from).year == current_year and (evaluation.evaluation_to).year == current_year:
						if evaluation.evaluation_classification in [ele.evaluation_classification for ele in self.current_year_evaluation]:
							current_evaluation = True
							emp_details["current_year_evaluation"] = evaluation.evaluation_classification
			if previous_evaluation == True and current_evaluation == True:
				emp_details["employee_no"]=emp
				final_employee_list.append(emp_details)
			print(final_employee_list,"======")
		return final_employee_list