# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class EmployeeResignationST(Document):
	def validate(self):
		self.validate_resignation_date()

	def validate_resignation_date(self):
		if self.last_working_days:
			today_month = getdate(nowdate()).month
			resignation_month = getdate(self.last_working_days).month

			if today_month == resignation_month:
				# today_date = nowdate().day
				last_working_days = getdate(self.last_working_days).day

				if last_working_days >= 11:
					frappe.throw(_("For this Month, Payroll is generated so you cann't apply for resignation"))
