# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, add_to_date


class AttendanceReconciliationST(Document):
	
	@frappe.whitelist()
	def fetch_attendance_details(self):
		reconciliation_data = []
		month_start_date, month_end_date = get_first_day(self.date), get_last_day(self.date)
		print(month_end_date,month_end_date.day)
		current_date = month_start_date
		for date in range(month_start_date.day, month_end_date.day+1):
			reconciliation_details = {}
			reconciliation_details["date"]=current_date
			current_date = add_to_date(current_date, days=1)
			print(reconciliation_details,"************")
			reconciliation_data.append(reconciliation_details)
		
		get_attendance = frappe.db.get_all("Attendance",
									 filters={"employee":self.employee_no,"attendance_date":["between",[month_start_date,month_end_date]]},
									 fields=["name","attendance_date","custom_attendance_type","custom_actual_delay","custom_actual_early","status","late_entry","early_exit"])
		if len(get_attendance)>0:
			for row in reconciliation_data:
				print(row)
				for attendance in get_attendance:
					if row.get("date") == attendance.attendance_date:
						row["type"]=attendance.status
						row["delay_in"]=attendance.custom_actual_delay
						row["early_out"]=attendance.custom_actual_early
		return reconciliation_data

