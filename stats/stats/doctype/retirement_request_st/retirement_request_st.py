# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from stats.salary import get_latest_salary_structure_assignment

class RetirementRequestST(Document):
	def validate(self):
		self.get_salary_details()

	def get_salary_details(self):
		salary_assignment = get_latest_salary_structure_assignment(self.employee_no, self.retirement_date)
		if len(salary_assignment) > 0:
			self.salary_structure_assignment_reference = salary_assignment
			salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
			ss = frappe.get_doc("Salary Structure", salary_structure)

			total_earnings = 0
			total_deductions = 0

			self.earning = []
			self.deduction = []
			for ear in ss.earnings:
				eos_ear = self.append("earning", {})
				eos_ear.earning = ear.salary_component
				eos_ear.amount = ear.amount
				total_earnings = total_earnings + eos_ear.amount

			for ded in ss.deductions:
				eos_ded = self.append("deduction", {})
				eos_ded.deduction = ded.salary_component
				eos_ded.amount = ded.amount
				total_deductions = total_deductions + eos_ded.amount

			
			self.total_monthly_salary = total_earnings
			self.total_monthly_deduction = total_deductions
			self.net_salary = self.total_monthly_salary - self.total_monthly_deduction

			salary_structure = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "salary_structure")
			ss = frappe.get_doc("Salary Structure", salary_structure)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_civil_employee(doctype, txt, searchfield, start, page_len, filters):
	employee = frappe.db.get_all("Employee", filters={"status":"Active"}, fields=["name", "custom_contract_type"])

	civil_employees = []
	for emp in employee:
		contract_type = frappe.db.get_value("Contract Type ST", emp.custom_contract_type, "contract")
		if contract_type == "Civil":
			employee_name = (emp.get('name'),)
			civil_employees.append(employee_name)
		else:
			continue

	return civil_employees
