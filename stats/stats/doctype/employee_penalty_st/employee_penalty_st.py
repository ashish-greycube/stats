# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, get_link_to_form, flt
from stats.api import get_base_amount_from_salary_structure_assignment

class EmployeePenaltyST(Document):
	def validate(self):
		self.fetch_penalty_details_from_violation_type()

	def on_submit(self):
		self.add_penalty_in_employee()
		self.create_additional_salary()


	def fetch_penalty_details_from_violation_type(self):
		prev_emp_penalty = frappe.db.count('Employee Penalty ST', {'employee': self.employee, 
															'violation_type':self.violation_type, 'name':['!=', self.name], 'docstatus':1})
		print(prev_emp_penalty, '---count-----------')
		base = get_base_amount_from_salary_structure_assignment(self.employee)
		if base == 0:
			frappe.throw(_("In Salary Structure Assigenment, Base Amount cann't be zero for {0} Employee").format(self.employee))
		else:
			if prev_emp_penalty == 0:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "First Time":
						self.action_type = pen.action_type
						self.deduction = flt(((base/30)*(pen.deduction/100)),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} First Time Penalty is not define.").format( self.violation_type))
			
			if prev_emp_penalty == 1:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "Second Time":
						self.action_type = pen.action_type
						self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Second Time Penalty is not define.").format( self.violation_type))

			if prev_emp_penalty == 2:
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					if pen.recurrence_type == "Third Time":
						self.action_type = pen.action_type
						self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Third Time Penalty is not define.").format( self.violation_type))

			if prev_emp_penalty >= 3:
				print(prev_emp_penalty, '---prev_emp_penalty')
				violation = frappe.get_doc("Violation ST", self.violation_type)
				for pen in violation.penalty:
					print(pen.recurrence_type, '---pen.recurrence_type')
					if pen.recurrence_type == "Fourth Time":
						self.action_type = pen.action_type
						self.deduction = flt((((base/30)*(pen.deduction/100)) / 100),2)
						break
					# else:
					# 	frappe.throw(_("In Violation type: {0} Fourth Time Penalty is not define.").format( self.violation_type))

			self.recurrence_count_of_violation = prev_emp_penalty + 1

	def add_penalty_in_employee(self):
		print("in side submit")
		employee = frappe.get_doc("Employee", self.employee)
		row =  employee.append("custom_penalty_history_details", {})
		row.penalty_reference = self.name
		row.penalty_date = nowdate()
		row.type_of_penalty = self.violation_type
		row.recurrence_type = self.recurrence_count_of_violation
		row.action_type = self.action_type
		print(row.penalty_reference, '---penalty_reference')
		employee.save(ignore_permissions = True)

	def create_additional_salary(self):
		base = get_base_amount_from_salary_structure_assignment(self.employee)
		penalty_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'penalty_deduction_component')
		additional_salary = frappe.new_doc("Additional Salary")
		additional_salary.employee = self.employee
		additional_salary.payroll_date = self.penalty_date
		additional_salary.salary_component = penalty_deduction_component
		additional_salary.amount = base * (self.deduction / 100)
		print(self.deduction, '----self.deduction', base, '======base')
		print(additional_salary.amount, '========== additional_salary.amount ===============')
		additional_salary.overwrite_salary_structure_amount = 0
		additional_salary.save(ignore_permissions = True)
		frappe.msgprint(_("Additional Salary {0} created." .format(get_link_to_form('Additional Salary', additional_salary.name))), alert=True)
		additional_salary.submit()