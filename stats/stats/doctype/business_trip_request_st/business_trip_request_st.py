# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class BusinessTripRequestST(Document):
	def validate(self):
		self.set_no_of_days()
	
	def set_no_of_days(self):
		if self.business_trip_start_date and self.business_trip_end_date:
			no_of_day = date_diff(self.business_trip_end_date, self.business_trip_start_date)
			self.no_of_days = no_of_day
		