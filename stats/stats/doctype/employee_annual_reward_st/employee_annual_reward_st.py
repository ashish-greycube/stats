# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.model.document import Document
from stats.salary import get_latest_salary_structure_assignment

class EmployeeAnnualRewardST(Document):
	def validate(self):
		self.calcualte_reward_value()

	def calcualte_reward_value(self):
		if len(self.employee_annual_reward_details) > 0:
			for reward in self.employee_annual_reward_details:
				salary_assignment = get_latest_salary_structure_assignment(reward.employee_no, self.creation_date)
				salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
				ss = frappe.get_doc("Salary Structure", salary_structure)

				reward_amount = 0
				for ear in ss.earnings:
					include_in_reward = frappe.db.get_value("Salary Component", ear.salary_component, "custom_include_in_reward")
					if include_in_reward == 1:
						reward_amount = reward_amount + ear.amount
				
				if reward.evaluation_classification == "Meet Expectation":
					reward.reward_value = reward_amount * 3
				elif reward.evaluation_classification == "Exceed Expectation":
					reward.reward_value = reward_amount * 4
				elif reward.evaluation_classification == "Highly Exceed Expectation":
					reward.reward_value = reward_amount * 6
	
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