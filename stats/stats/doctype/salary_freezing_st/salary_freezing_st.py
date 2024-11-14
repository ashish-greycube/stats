# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date,get_first_day,getdate,nowdate, get_link_to_form

class SalaryFreezingST(Document):
	def validate(self):
		self.validate_salary_freezing_dates()
		# self.create_additonal_salary_for_salary_freezing()

	def on_submit(self):
		self.create_additonal_salary_for_salary_freezing()

	def validate_salary_freezing_dates(self):
		if self.salary_freezing_start_date > self.salary_freezing_end_date:
			frappe.throw(_("Salary Freezing Start Date Cann't Be Greater Than End Date."))

	def create_additonal_salary_for_salary_freezing(self):
		freezing_month_dates = []
		month_date = self.salary_freezing_start_date
		while(self.salary_freezing_start_date <= month_date and self.salary_freezing_end_date >= month_date):
			month_start_date=get_first_day(month_date)
			if month_start_date not in freezing_month_dates:
				freezing_month_dates.append(month_start_date)

			month_date = add_to_date(month_date, months=1)

		for freezing in freezing_month_dates:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", nowdate()], "employee":self.employee_no}, 
								  order_by = "from_date desc", limit=1)
			
			print
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
				
				contract_type = frappe.db.get_value('Employee', self.employee_no, 'custom_contract_type')

				if not contract_type:
					frappe.throw(_("No Contract Type is defined for {0} employee").format(self.employee_no))
				
				contract = frappe.db.get_value('Contract Type ST', contract_type, 'contract')

				total_freezing_deduction = 0

				total_earning = 0
				total_deduction = 0

				for ear in ss.earnings:
					total_earning = total_earning + ear.amount

				for ded in ss.deductions:
					total_deduction = total_deduction + ded.amount

				if contract == "Civil":
					total_freezing_deduction = (total_earning - total_deduction) / 2
				elif contract == "Direct":
					total_freezing_deduction = total_earning / 2

				
				if total_freezing_deduction > 0:
					salary_freezing_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'salary_freezing_deduction_component')
					print(salary_freezing_deduction_component, '--salary_freezing_deduction_component')
					if not salary_freezing_deduction_component:
						frappe.throw(_("Please Set Salary Freezing Deduction Component in Stats Settings Doctype"))
					else:
						additional_salary = frappe.new_doc("Additional Salary")
						additional_salary.employee = self.employee_no
						additional_salary.payroll_date = freezing
						additional_salary.salary_component = total_freezing_deduction
						additional_salary.overwrite_salary_structure_amount = 0
						additional_salary.amount = total_freezing_deduction
						additional_salary.save(ignore_permissions=True)
						additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Salary Freezing Deduction'.format(nowdate()))
						frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, self.name), alert=1)
						additional_salary.submit()


		# print(freezing_month_dates, '=================freezing_month_dates==========================')

	
