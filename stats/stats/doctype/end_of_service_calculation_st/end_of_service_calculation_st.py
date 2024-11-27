# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from frappe.utils import add_to_date, date_diff
from stats.salary import get_latest_salary_structure_assignment
from hrms.hr.doctype.leave_application.leave_application import get_leave_details

class EndofServiceCalculationST(Document):
	def validate(self):
		self.get_salary_details()
		self.calculate_end_of_service_due_amount()
		self.calculate_vacation_due_amount()

	def get_salary_details(self):
		salary_assignment = get_latest_salary_structure_assignment(self.employee, self.last_working_date)
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

	def calculate_end_of_service_due_amount(self):

		########## working days calculation #########

		joining_date = self.joining_date
		last_working_date = self.last_working_date
		total_no_of_working_days = date_diff(last_working_date, joining_date)
		no_of_days_in_last_year_of_service = total_no_of_working_days % 360
		no_of_full_years_in_service = total_no_of_working_days - no_of_days_in_last_year_of_service


		self.total_no_of_working_days = total_no_of_working_days
		self.no_of_full_years_in_service = no_of_full_years_in_service
		self.no_of_days_in_last_year_of_service = no_of_days_in_last_year_of_service

		####### due amount calculation ########

		full_salary = self.total_monthly_salary
		half_salary = full_salary / 2
		years = no_of_full_years_in_service / 360

		per_year_due_amount = 0
		per_day_due_amount = 0
		eos_due_amount = 0

		regination_type = frappe.get_doc("Resignation Type ST", self.resignation_type)

		if regination_type.is_it_resignation == 1:
			if self.total_no_of_working_days > 720 and self.total_no_of_working_days < 1800:
				per_year_due_amount = (half_salary / 3)
				total_years_due_amount =per_year_due_amount * years
				per_day_due_amount = per_year_due_amount/360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

			elif self.total_no_of_working_days > 1800:
				per_year_due_amount = full_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

			else:
				eos_due_amount = 0

		elif regination_type.is_it_not_renewal_of_contract == 1:
			if self.total_no_of_working_days > 1800:
				per_year_due_amount = half_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount
			else:
				per_year_due_amount = full_salary
				total_years_due_amount = per_year_due_amount * years
				per_day_due_amount = per_year_due_amount /360
				last_year_days_due_amount = per_day_due_amount * self.no_of_days_in_last_year_of_service

				eos_due_amount = total_years_due_amount + last_year_days_due_amount

		self.per_day_eos_due_amount = per_day_due_amount
		self.per_year_eos_due_amount = per_year_due_amount
		self.end_of_service_due_amount = eos_due_amount

	def calculate_vacation_due_amount(self):
		########## vacation days calculation #########

		contract_type = frappe.db.get_value("Employee", self.employee, "custom_contract_type")
		considered_vacation_days = frappe.db.get_value("Contract Type ST", contract_type, "considered_vacation_days")
		salary_assignment = get_latest_salary_structure_assignment(self.employee, self.last_working_date)
		total_monthly_salary = frappe.db.get_value("Salary Structure Assignment", salary_assignment, "base")
		per_day_salary = total_monthly_salary / 30
		
		if considered_vacation_days:
			self.considered_vacation_days = considered_vacation_days

			leave_types = frappe.db.sql_list("select name from `tabLeave Type` where custom_allow_encasement_end_of_service = 1 order by name asc")

			# available_leave = get_leave_details(self.employee, "2024-11-26")
			available_leave = get_leave_details(self.employee, self.last_working_date)
			if len(available_leave["leave_allocation"]) > 0:
				total_considered_vacation_days = 0
				for leave_type in leave_types:
					remaining = 0
					if leave_type in available_leave["leave_allocation"]:
						remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
					total_considered_vacation_days = total_considered_vacation_days + remaining

					print(leave_type, "===leave_type",remaining, "====remaining")
					print(total_considered_vacation_days, "==total_considered_vacation_days")

				self.vacation_balance = total_considered_vacation_days

				if self.considered_vacation_days < self.vacation_balance:
					self.vacation_due_amount = per_day_salary * total_considered_vacation_days
				else:
					self.vacation_due_amount = per_day_salary * total_considered_vacation_days

			else:
				frappe.throw(_("Leave Allocation is not found for {0} employee for {1} date.").format(self.employee, self.last_working_date))

