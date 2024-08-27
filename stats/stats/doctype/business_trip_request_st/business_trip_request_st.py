# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import date_diff
from stats.api import fetch_employee_per_diem_amount


class BusinessTripRequestST(Document):
	def validate(self):
		self.set_no_of_days()
		self.validate_no_of_days()
		self.set_total_employee_amount_for_trip()
	
	def set_no_of_days(self):
		if self.business_trip_start_date and self.business_trip_end_date:
			no_of_day = date_diff(self.business_trip_end_date, self.business_trip_start_date)
			self.no_of_days = no_of_day
	def validate_no_of_days(self):
		if self.trip_remaining_balance :
			if self.trip_remaining_balance < self.no_of_days :
				frappe.throw(_("No of days cannot be greater than Trip remaining balance"))

	def set_total_employee_amount_for_trip(self):
		amount_for_trip = fetch_employee_per_diem_amount(self.employee_no,self.no_of_days)
		print(amount_for_trip,"amount")
		self.total_employee_amount_for_trip = amount_for_trip

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
	doc.run_method("calculate_taxes_and_totals")
	doc.save()	
	return doc.name