# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe import _
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee, validate_dates
from frappe.utils import get_link_to_form, getdate, cstr, get_datetime
from frappe.utils.data import get_date_str


class AttendanceRequestST(Document):
	def validate(self):
		validate_active_employee(self.employee_no)
		# validate_dates(self, self.request_date, self.request_date)
		self.validate_request_overlap()
		# check against salary freezzing / scholarship <---- Pending

	def on_submit(self):
		self.create_employee_checkin_records()
		
	def on_cancel(self):
		self.delete_employee_checkin_records()

	def validate_request_overlap(self):
		exists_request = frappe.db.exists("Attendance Request ST", {"request_date": self.request_date,"employee_no": self.employee_no,"attendance_type": self.attendance_type})
		print(exists_request,"--------------------")
		if exists_request != None and exists_request != self.name:
			frappe.throw(_("This employee already has a request with the same date and attendance type <br><b>{0}</b>").format(get_link_to_form("Attendance Request ST", exists_request)))
	
	def create_employee_checkin_records(self):
		shift_name = frappe.db.get_value("Employee",self.employee_no,"default_shift")
		
		if shift_name:
			shift_start_time = frappe.db.get_value("Shift Type",shift_name,"start_time")
			shift_end_time = frappe.db.get_value("Shift Type",shift_name,"end_time")
		else:
			frappe.throw("Please set default shift in employee")

		employee_checkin_doc = frappe.new_doc("Employee Checkin")
		employee_checkin_doc.employee = self.employee_no
		employee_checkin_doc.log_type = self.attendance_type
		
		if self.attendance_type == "IN":
			employee_checkin_doc.time = get_datetime(get_date_str(self.request_date) + " " + cstr(shift_start_time))
		elif self.attendance_type == "OUT":
			employee_checkin_doc.time = get_datetime(get_date_str(self.request_date) + " " + cstr(shift_end_time))
		employee_checkin_doc.custom_attendance_request_st = self.name
		employee_checkin_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Employee Checkin is created <b>{0}</b>").format(get_link_to_form("Employee Checkin",employee_checkin_doc.name)),alert=True)

	def delete_employee_checkin_records(self):
		employee_checkin = frappe.db.get_all("Employee Checkin",
									   filters={"custom_attendance_request_st":self.name},
									   fields=["name"])
		if len(employee_checkin)>0:
			for checkin in employee_checkin:
				employee_checkin_doc = frappe.get_doc("Employee Checkin",checkin.name)
				employee_checkin_doc.delete()
				frappe.msgprint(_("Employee Checkin <b>{0}</b> is deleted.").format(checkin.name),alert=True)