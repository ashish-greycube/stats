# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import date_diff
from stats.api import fetch_employee_per_diem_amount
from stats.budget import get_budget_account_details
from erpnext.accounts.utils import get_fiscal_year

class BusinessTripRequestST(Document):
	def validate(self):
		self.set_no_of_days()
		self.validate_no_of_days()
		self.set_total_employee_amount_for_trip()
		self.check_trip_days_not_in_personal_vacation()
		self.set_no_of_trip_days_in_employee()	
		self.check_availabel_balance_for_department()
	
	def check_trip_days_not_in_personal_vacation(self):
		leave_details=	frappe.db.sql(
					"""
					select
						name, leave_type, posting_date, from_date, to_date, total_leave_days, half_day_date
					from `tabLeave Application`
					where employee = %(employee)s and docstatus < 2 and status in ('Open', 'Approved')
					and to_date >= %(from_date)s and from_date <= %(to_date)s
					""",
					{
						"employee": self.employee_no,
						"from_date": self.business_trip_start_date,
						"to_date": self.business_trip_end_date,
					},
					as_dict=1,
				)
		if len(leave_details)>0:
			leave_names=",".join(i.name for i in leave_details)
			frappe.throw(_("You have leave application <b>{0}</b> during your business trip days. It is not allowed.").format(leave_names))

	def set_no_of_trip_days_in_employee(self):
		if self.status=='Approved':
			custom_no_of_business_trip_days_remaining = frappe.db.get_value('Employee', self.employee_no, 'custom_no_of_business_trip_days_remaining')
			no_of_business_trip_days_remaining=custom_no_of_business_trip_days_remaining-self.no_of_days
			frappe.db.set_value('Employee', self.employee_no, 'custom_no_of_business_trip_days_remaining', no_of_business_trip_days_remaining)
			frappe.msgprint(_("Employee No of business trip days is updated to {0}").format(no_of_business_trip_days_remaining), alert=1)			

	def set_no_of_days(self):
		if self.business_trip_start_date and self.business_trip_end_date:
			no_of_day = date_diff(self.business_trip_end_date, self.business_trip_start_date)
			self.no_of_days = no_of_day
	def validate_no_of_days(self):
		if self.no_of_days :
			if self.trip_remaining_balance < self.no_of_days :
				frappe.throw(_("No of days cannot be greater than Trip remaining balance"))

	def set_total_employee_amount_for_trip(self):
		amount_for_trip = fetch_employee_per_diem_amount(self.employee_no,self.no_of_days)
		print(amount_for_trip,"amount")
		self.total_employee_amount_for_trip = amount_for_trip

	def on_submit(self):
		self.check_availabel_balance_for_department()
		if self.get("workflow_state") and self.workflow_state != "Approved":
			frappe.throw(_("You cannot submit before DM has Approved"))

	def check_availabel_balance_for_department(self):
		if self.main_department:
			department_cost_center = frappe.db.get_value('Department', self.main_department, 'custom_department_cost_center')
			company = erpnext.get_default_company()
			company_business_trip_budget_expense_account = frappe.db.get_value("Company",company,"custom_business_trip_budget_expense_account")
			fiscal_year = get_fiscal_year(self.creation_date)[0]
			print(department_cost_center, '--department_cost_center', company, '--company', fiscal_year, '--fiscal_year')
			if department_cost_center:
				acc_details = get_budget_account_details(department_cost_center,company_business_trip_budget_expense_account,fiscal_year)
				print(acc_details.available, '---acc_details.available')
				if acc_details:
					if self.total_employee_amount_for_trip > acc_details.available:
						frappe.throw(_('There is no budget amount'))
				else:
					frappe.throw(_('No Budget Found.'))

@frappe.whitelist()
def create_ticket_request_from_business_trip_request(source_name, target_doc=None):
	print("="*10)
	btr_doc = frappe.get_doc("Business Trip Request ST",source_name)
	
	def set_missing_values(source, target):

		target.business_trip_reference=source_name
	
	doc = get_mapped_doc('Business Trip Request ST', source_name, {
		'Business Trip Request ST': {
			'doctype': 'Ticket Request ST',
			# 'field_map': {
			# 	'agent_name':'name',
			# },			
			'validation': {
				'docstatus': ['!=', 2]
			}
		}		
	}, target_doc,set_missing_values)
	doc.run_method("set_missing_values")
	doc.save()	
	return doc.name

@frappe.whitelist()
def create_employee_task_completion_from_business_trip_request(source_name, target_doc=None):
	print("="*10)
	btr_doc = frappe.get_doc("Business Trip Request ST",source_name)
	
	def set_missing_values(source, target):

		target.business_trip_reference=source_name
		trip_cost_template=frappe.db.get_single_value('Stats Settings ST', 'default_trip_cost_template')
		print('trip_cost_template',trip_cost_template)
		if not trip_cost_template:
			frappe.throw(_("Please set 'default trip cost template' in Stats Settings"))
		tct_doc = frappe.get_doc("Trip Cost Template ST",trip_cost_template)
		for tc_detail in tct_doc.trip_cost_template_details:
			target.append('trip_cost_detail',{'element':tc_detail.element,'payment_method':tc_detail.payment_method})
		target.trip_cost_template=trip_cost_template

	doc = get_mapped_doc('Business Trip Request ST', source_name, {
		'Business Trip Request ST': {
			'doctype': 'Employee Task Completion ST',
			# 'field_map': {
			# 	'agent_name':'name',
			# },			
			'validation': {
				'docstatus': ['!=', 2]
			}
		}		
	}, target_doc,set_missing_values)
	doc.run_method("set_missing_values")
	print('doc',doc.get('trip_cost_detail'))
	doc.save()	
	return doc.name
