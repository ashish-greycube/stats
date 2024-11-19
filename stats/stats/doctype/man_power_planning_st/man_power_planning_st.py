# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ManPowerPlanningST(Document):
	def validate(self):
		self.set_job_no_in_employee()
		self.change_position_status_in_job_details()

	def set_job_no_in_employee(self):
		if len(self.job_details) > 0:
			for job in self.job_details:
				if job.employee_no:
					employee = frappe.get_doc('Employee', job.employee_no)
					if employee.custom_job_no == None:
						employee.custom_job_no = job.job_no
						employee.save(ignore_permissions=True)
						frappe.msgprint(_("In Employee {0} Job No set to {1}").format(employee.name, job.job_no), alert=True)
				else:
					pass

	def change_position_status_in_job_details(self):
		if len(self.job_details):
			for job in self.job_details:
				if job.employee_no:
					job.position_status = "Filled"