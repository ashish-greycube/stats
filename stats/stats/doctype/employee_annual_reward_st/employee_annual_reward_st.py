# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.model.document import Document


class EmployeeAnnualRewardST(Document):
	
	@frappe.whitelist()
	def fetch_employee_based_on_classification(self):
		employee_evaluation_list = frappe.db.get_all("Employee Evaluation ST",
											   filters={"evaluation_type":self.evaluation_type},
											   fields=["name","employee_no","evaluation_from","evaluation_classification","final_evaluation"])
		
		final_list = []
		if len(employee_evaluation_list)>0:
			for record in employee_evaluation_list:
				emp_details = {}
				if (record.evaluation_from).year == cint(self.reward_year):
					if record.evaluation_classification in [ele.evaluation_classification for ele in self.select_evaluation]:
						emp_details["employee_no"]=record.employee_no
						emp_details["evaluation_classification"]=record.evaluation_classification
						emp_details["final_evaluation"]=record.final_evaluation

						final_list.append(emp_details)
		print(final_list,'---------')
		return final_list