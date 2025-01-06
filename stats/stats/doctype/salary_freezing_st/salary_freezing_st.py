# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date,get_first_day,getdate,nowdate, get_link_to_form, cint
from stats.salary import get_latest_salary_structure_assignment

class SalaryFreezingST(Document):
	def validate(self):
		self.validate_salary_freezing_dates()
		# self.create_salary_structure_and_assignments()

	def on_submit(self):
		self.create_salary_structure_and_assignments()

	def validate_salary_freezing_dates(self):
		if self.salary_freezing_start_date > self.salary_freezing_end_date:
			frappe.throw(_("Salary Freezing Start Date Cann't Be Greater Than End Date."))
		
		if ((getdate(self.salary_freezing_start_date).month == getdate(self.salary_freezing_end_date).month) and 
			(getdate(self.salary_freezing_start_date).year == getdate(self.salary_freezing_end_date).year)):
			frappe.throw(_("Salary Freezing Start Date And End Date Cann't Be in same month"))


	def create_salary_structure_and_assignments(self):
		if not self.grade:
			frappe.throw(_("Grade is Mandatory Field."))

		payroll_date = frappe.db.get_single_value('Stats Settings ST', 'every_month_payroll_date')
		# basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')
		contract_type = frappe.db.get_value("Contract Type ST", self.contract_type, 'contract')

		basic_salary_component = frappe.db.get_value("Employee Grade", self.grade, 'custom_basic_salary_component')

		if payroll_date == None:
			frappe.throw(_("Please Set Every Month Payroll Date In Stats Settings."))

		if contract_type == None:
			frappe.throw(_("Please Set Contract Type."))

		prev_salary_assignment = get_latest_salary_structure_assignment(self.employee_no, self.salary_freezing_start_date)
		salary_structure = frappe.db.get_value("Salary Structure Assignment", prev_salary_assignment, "salary_structure")
		prev_ss = frappe.get_doc("Salary Structure", salary_structure)

		###### new frezzing salary structure #######

		new_ss = frappe.new_doc("Salary Structure")
		new_ss.__newname = self.employee_no + "/" + self.name
		new_ss.name = self.employee_no + "/" + self.name

		prev_total_deduction = 0
		if len(prev_ss.deductions) > 0:
			for ded in prev_ss.deductions:
				deduction = new_ss.append("deductions", {})
				deduction.salary_component = ded.salary_component
				deduction.amount_based_on_formula = 0
				deduction.is_tax_applicable = 0
				deduction.depends_on_payment_days = 0

				if contract_type == "Civil":
					deduction.amount = 0
				elif contract_type == "Direct":
					deduction.amount = ded.amount

				prev_total_deduction = prev_total_deduction + ded.amount

		new_total_earnings = 0
		prev_total_earnings = 0
		if len(prev_ss.earnings) > 0:
			for ear in prev_ss.earnings:
					earning = new_ss.append("earnings", {})
					earning.salary_component = ear.salary_component
					# earning.amount = ear.amount / 2
					earning.amount_based_on_formula = 0
					earning.is_tax_applicable = 0
					earning.depends_on_payment_days = 0

					if contract_type == "Direct":
						earning.amount = ear.amount / 2
					elif contract_type == "Civil":
						if ear.salary_component == basic_salary_component:
							earning.amount = (ear.amount - prev_total_deduction) / 2
						else:
							earning.amount = ear.amount / 2

					prev_total_earnings = prev_total_earnings + ear.amount
					new_total_earnings = new_total_earnings + earning.amount

		new_ss.save(ignore_permissions=True)
		frappe.msgprint(_("Salary Structure {0} is created."
					.format(get_link_to_form('Salary Structure', new_ss.name))), alert=True)
		new_ss.submit()

		######### salary structure assignment #########

		if getdate(self.salary_freezing_start_date).day < cint(payroll_date):
			print("start before payroll")
			self.create_salary_structure_assignment(new_ss.name, get_first_day(self.salary_freezing_start_date), new_total_earnings)		
		elif getdate(self.salary_freezing_start_date).day >= cint(payroll_date):
			print("start after payroll")
			next_month = add_to_date(self.salary_freezing_start_date,months=1)
			self.create_salary_structure_assignment(new_ss.name, get_first_day(next_month), new_total_earnings)
		else:
			pass

		if getdate(self.salary_freezing_end_date).day < cint(payroll_date):
			print("end before payroll")
			self.create_salary_structure_assignment(prev_ss.name, get_first_day(self.salary_freezing_end_date), prev_total_earnings)
		elif getdate(self.salary_freezing_end_date).day >= cint(payroll_date):
			print("end after payroll")
			next_month = add_to_date(self.salary_freezing_end_date,months=1)
			self.create_salary_structure_assignment(prev_ss.name, get_first_day(next_month), prev_total_earnings)
		else:
			pass		


	def create_salary_structure_assignment(self, salary_structure, from_date, base):
		assignment = frappe.new_doc("Salary Structure Assignment")
		assignment.employee = self.employee_no
		assignment.salary_structure = salary_structure
		assignment.from_date = getdate(from_date)
		assignment.base = base

		assignment.save(ignore_permissions=True)
		frappe.msgprint(_("Salary Structure Assignment {0} created." .format(get_link_to_form('Salary Structure Assignment', assignment.name))), alert=True)
		assignment.submit()

	
