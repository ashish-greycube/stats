# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr
from stats.hr_utils import check_if_holiday_between_applied_dates

class TrainingRequestST(Document):
	def validate(self):
		print("++++++++++++++++++++++++++++++=")
	def on_update_after_submit(self):
		print("--------------------------------")
		self.create_future_attendance_for_business_trip_time()

	def create_future_attendance_for_business_trip_time(self):
		if self.status == "Accepted":
			print("In condition 1")
			days = date_diff(self.training_end_date,self.training_start_date)
			print(days)
			for day in range (days+1):
				attendance_date = add_to_date(self.training_start_date,days=day)
				check_holiday = check_if_holiday_between_applied_dates(self.employee_no,attendance_date,attendance_date)
				if check_holiday == False:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.employee_no
					attendance_doc.attendance_date = attendance_date
					attendance_doc.custom_attendance_type = "In Training"
					employee_shift = frappe.db.get_value("Employee",self.employee_no,"default_shift")
					shift_start_time = frappe.db.get_value("Shift Type",employee_shift,"start_time")
					shift_end_time = frappe.db.get_value("Shift Type",employee_shift,"end_time")
					attendance_doc.shift = employee_shift
					attendance_doc.in_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_start_time))
					attendance_doc.out_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_end_time))
					attendance_doc.status = "Present"
					attendance_doc.save(ignore_permissions=True)
					print(attendance_doc.name,"---")
					attendance_doc.submit()
				else :
					pass
