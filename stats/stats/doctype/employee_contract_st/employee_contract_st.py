# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from frappe.utils import add_to_date,add_years
from stats.api import get_monthly_salary_from_job_offer

class EmployeeContractST(Document):
	def validate(self):
		self.validate_trial_period()

	def on_submit(self):
		self.create_salary_structure()

	def validate_trial_period(self):	
		if self.job_offer_reference:
			monthly_salary = get_monthly_salary_from_job_offer(self.job_offer_reference)
			self.total_monthly_salary = monthly_salary
		if self.contract_start_date:
			self.test_period_end_date = add_to_date(self.contract_start_date, months=3)
			self.contract_end_date = add_years(self.contract_start_date, 1)
			if self.test_period_renewed == "Yes":
				self.end_of_new_test_period = add_to_date(self.test_period_end_date, months=3)
			else:
				self.end_of_new_test_period = None

	def on_update_after_submit(self):
		if self.test_period_renewed == "Yes":
			self.end_of_new_test_period = add_to_date(self.test_period_end_date, months=3)

	def create_salary_structure(self):
		if self.contract_type:
			salary_structure = frappe.new_doc("Salary Structure")
			salary_structure.__newname = self.employee_no + "/" + self.name
			salary_structure.name = self.employee_no + "/" + self.name
			salary_structure.custom_employee_contract_ref = self.name
			salary_structure.custom_employee_no = self.employee_no
			salary_structure.custom_contract_start_date = self.contract_start_date

			if len(self.earning):
				for ear in self.earning:
					earning = salary_structure.append("earnings", {})
					earning.salary_component = ear.earning
					earning.amount = ear.amount
					earning.amount_based_on_formula = 0
					earning.is_tax_applicable = 0
			
			if len(self.deduction):
				for ded in self.deduction:
					deduction = salary_structure.append("deductions", {})
					deduction.salary_component = ded.deduction
					deduction.amount = ded.amount
					deduction.amount_based_on_formula = 0
					deduction.is_tax_applicable = 0
			
			salary_structure.save(ignore_permissions=True)

			frappe.msgprint(_("Salary Structure {0} is created."
					 .format(get_link_to_form('Salary Structure', salary_structure.name))), alert=True)
			
			salary_structure.submit()

@frappe.whitelist()
def get_salary_details(parent, parenttype):

	earning = frappe.get_all(
		"Earning Amount ST",
		fields=[
			"earning",
			"abbr",
			"formula",
			"amount"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	deduction = frappe.get_all(
		"Deduction Amount ST",
		fields=[
			"deduction",
			"abbr",
			"formula",
			"amount"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)

	return earning, deduction