# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_link_to_form,add_to_date
from stats.api import calculate_actual_degree_based_on_weight


class EmployeeEvaluationST(Document):

	def validate(self):
		calculate_actual_degree_based_on_weight(self.employee_personal_goals)
		calculate_actual_degree_based_on_weight(self.employee_job_goals)
		calculate_actual_degree_based_on_weight(self.employee_management_skills)
		self.calculate_evaluation_summary()

	def calculate_evaluation_summary(self):
		total_degree_of_personal_goals = 0
		total_degree_of_job_goals = 0
		total_degree_of_management_skills = 0

		if len(self.employee_personal_goals)>0:
			for row in self.employee_personal_goals:
				if row.actual_degree_based_on_weight:
					total_degree_of_personal_goals = total_degree_of_personal_goals + row.actual_degree_based_on_weight
		if len(self.employee_job_goals)>0:
			for goal in self.employee_job_goals:
				if goal.actual_degree_based_on_weight:
					total_degree_of_job_goals = total_degree_of_job_goals + goal.actual_degree_based_on_weight
		if len(self.employee_management_skills)>0:
			for skill in self.employee_management_skills:
				if skill.actual_degree_based_on_weight:
					total_degree_of_management_skills = total_degree_of_management_skills + skill.actual_degree_based_on_weight

		self.personal_goals = total_degree_of_personal_goals
		self.job_goals = total_degree_of_job_goals
		self.management_skills = total_degree_of_management_skills
		
		stats_settings_doc = frappe.get_doc("Stats Settings ST")
		final_evaluation = 0
		if len(self.employee_management_skills)>0:
			final_evaluation = ((total_degree_of_personal_goals * stats_settings_doc.management_employee_personal_goals / 100) + 
					   (total_degree_of_job_goals * stats_settings_doc.management_job_goals / 100) + 
					   (total_degree_of_management_skills * stats_settings_doc.management_skills / 100))
		
		else :
			final_evaluation = ((total_degree_of_personal_goals * stats_settings_doc.normal_employee_personal_goals / 100) + 
					   (total_degree_of_job_goals * stats_settings_doc.normal_job_goals / 100))
			
		self.final_evaluation = final_evaluation
		if final_evaluation > 0:
			for row in stats_settings_doc.evaluation_slots:
				if final_evaluation >= row.lower_range and final_evaluation <= row.upper_range:
					self.evaluation_classification = row.evaluation_classification

	def on_submit(self):
		if self.action:
			if self.action == "Hire":
				frappe.db.set_value("Employee",self.employee_no,"custom_test_period_completed","Yes")
				frappe.msgprint(_("Test period is completed for employee {0}").format(self.employee_no),alert=1)

			employee_contract_doc = frappe.get_doc("Employee Contract ST",self.employee_contract_reference)
			if self.action == "Separate":
				frappe.db.set_value("Employee",self.employee_no,"status","Left")
				employee_contract_doc.status = "Separated"
				employee_contract_doc.save(ignore_permissions = True)
				frappe.msgprint(_("Employee Contract {0} status is changed to <b>{1}</b> ").format(get_link_to_form("Employee Contract ST",self.employee_contract_reference),"Separated"),alert=1)

			elif self.action == "Renew Test Period":
				employee_contract_doc.test_period_renewed = "Yes"
				employee_contract_doc.status = "Renewed"
				employee_contract_doc.end_of_new_test_period = add_to_date(employee_contract_doc.test_period_end_date, months=3)
				employee_contract_doc.save(ignore_permissions = True)
				frappe.msgprint(_("Employee Contract {0} is <b>{1}</b> ").format(get_link_to_form("Employee Contract ST",self.employee_contract_reference),"Renewed"),alert=1)
	
	@frappe.whitelist()
	def fetch_employee_different_goals(self):
		employee_personal_goal_details = None
		if self.employee_no:
			employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
											  filters={"employee_no":self.employee_no,"docstatus":1},
											  fields=["name"])
			if len(employee_personal_goal)>0:
				employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
				employee_personal_goal_details = employee_personal_goal_doc.personal_goals

		evaluation_template_details = None
		if self.grade:
			evaluation_template = frappe.db.get_all("Employee Evaluation Template ST",
										   filters={"grade":self.grade},
										   fields=["name"])
			if len(evaluation_template)>0:
				evaluation_template_doc = frappe.get_doc("Employee Evaluation Template ST",evaluation_template[0].name)
				evaluation_template_details = evaluation_template_doc.job_goals
				print(evaluation_template_details,"------------")
		if self.designation:
			designation_doc = frappe.get_doc("Designation",self.designation)
			management_skills = designation_doc.custom_management_skills
			
		return employee_personal_goal_details, evaluation_template_details, management_skills
			
