# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, add_to_date,get_weekday, getdate, get_link_to_form
from datetime import date


class AttendanceReconciliationST(Document):
	
	def validate(self):
		self.validate_reason_for_reconciliation()
		self.calculate_and_update_attendance()
	
	# def on_submit(self):
	# 	self.calculate_and_update_attendance()

	def validate_reason_for_reconciliation(self):
		print("------------")
		if len(self.attendance_reconciliation_details)>0:
			balance_to_consume = 0
			for row in self.attendance_reconciliation_details:
				if row.type == "Weekly Off":
					if row.reason != "":
						frappe.throw(_("# Row {0}: You cannot select any reason for weekly off.".format(row.idx)))

				if row.type == "Present":
					if (row.delay_in == 0 and row.early_out == 0) and row.reason != "":
						frappe.throw(_("# Row {0}: You cannot select any reason as there is no need of reconciliation".format(row.idx)))

				if row.reason == "Personal Permission":
					if row.delay_in > 0 or row.early_out > 0:
						pass
					else:
						frappe.throw(_("# Row{0}: You cannot select reason <b>{1}</b>".format(row.idx,row.reason)))

				if row.reason == "Deduct from Extra Balance":
					if row.delay_in == 0 and row.early_out > 0:
						pass
					else :
						frappe.throw(_("# Row{0}: You cannot select reason <b>{1}</b> because you do not have extra balance".format(row.idx,row.reason)))

				if row.reason == "Deduct From Permission Balance":
					print("++++++++++++")
					if row.delay_in > 0 or row.early_out > 0:
						balance_to_consume = balance_to_consume + row.balance_to_be_consumed_in_minutes
					else:
						frappe.throw(_("# Row{0}: You cannot select reason <b>{1}</b>".format(row.idx,row.reason)))
			print(balance_to_consume)
			self.total_to_be_consumed_balance = balance_to_consume
			if balance_to_consume > self.total_available_permission_balance :
				frappe.throw(_("You do not have enough permission balance. Please readuse Balance To Be Consumed from any row <br>Your available balance is <b>{0}</b> and your consumed balance is <b>{1}</b>".format(self.total_available_permission_balance,self.total_to_be_consumed_balance)))

	def calculate_and_update_attendance(self):
		print('-'*10)
		if len(self.attendance_reconciliation_details)>0:
			for row in self.attendance_reconciliation_details:
				if row.reason == "Personal Permission":
					if row.delay_in > 0 or row.early_out > 0:
						print('e-'*10)
						attendance_doc = frappe.get_doc("Attendance",row.attendance_reference)
						attendance_doc.custom_net_working_minutes = row.actual_working_minutes + (row.delay_in or 0) + (row.early_out or 0)
						attendance_doc.custom_reconciliation_method = row.reason
						attendance_doc.custom_attendance_type = "Present Due To Reconciliation"
						attendance_doc.custom_difference_in_working_minutes = attendance_doc.custom_net_working_minutes - row.actual_working_minutes
						if attendance_doc.custom_difference_in_working_minutes >= 0:
							attendance_doc.status = "Present"
						attendance_doc.add_comment("Comment",text="Net Working Hours are calculated based on Attendance Reconciliation {0}".format(get_link_to_form("Attendance Reconciliation ST",self.name)))
						print('8-'*10)
						attendance_doc.save(ignore_permissions=True)
			
			for row in self.attendance_reconciliation_details:
				if row.reason == "Deduct from Extra Balance":
					if row.delay_in == 0 and row.early_out > 0:
						if row.extra_minutes > 0:
								attendance_doc = frappe.get_doc("Attendance",row.attendance_reference)
								attendance_doc.custom_net_working_minutes = row.actual_working_minutes
								attendance_doc.custom_reconciliation_method = row.reason
								attendance_doc.custom_attendance_type = "Present Due To Reconciliation"
								attendance_doc.custom_difference_in_working_minutes = attendance_doc.custom_net_working_minutes - row.actual_working_minutes
								if attendance_doc.custom_difference_in_working_minutes >= 0:
									attendance_doc.status = "Present"								
								attendance_doc.add_comment("Comment",text="Net Working Hours are calculated based on Attendance Reconciliation {0}".format(get_link_to_form("Attendance Reconciliation ST",self.name)))
								attendance_doc.save(ignore_permissions=True)

			for row in self.attendance_reconciliation_details:
				if row.reason == "Deduct From Permission Balance":
					if row.delay_in > 0 or row.early_out > 0:
						attendance_doc = frappe.get_doc("Attendance",row.attendance_reference)
						attendance_doc.custom_net_working_minutes = row.actual_working_minutes + row.balance_to_be_consumed_in_minutes
						attendance_doc.custom_reconciliation_method = row.reason
						attendance_doc.custom_attendance_type = "Present Due To Reconciliation"
						attendance_doc.custom_difference_in_working_minutes = attendance_doc.custom_net_working_minutes - row.actual_working_minutes
						if attendance_doc.custom_difference_in_working_minutes >= 0:
							attendance_doc.status = "Present"								
						attendance_doc.add_comment("Comment",text="Net Working Hours are calculated based on Attendance Reconciliation {0}".format(get_link_to_form("Attendance Reconciliation ST",self.name)))
						attendance_doc.save(ignore_permissions=True)

						contract_type_name = attendance_doc.custom_contract_type
						contract_type = frappe.db.get_value("Contract Type ST",contract_type_name,"contract")

						if contract_type == "Direct":
							new_available_balance = self.total_available_permission_balance - self.total_to_be_consumed_balance
							frappe.db.set_value("Employee",self.employee_no,"custom_permission_balance_per_year",new_available_balance)

	@frappe.whitelist()
	def fetch_attendance_details(self):
		
		month_number_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
		}
		
		from datetime import date

		current_month_no = month_number_mapping.get(self.current_year_month)
		month_start_date = date(year=getdate(self.date).year, month=current_month_no, day=1)
		month_end_date = get_last_day(month_start_date)
		current_date = month_start_date

		reconciliation_data = []
		for date in range(month_start_date.day, month_end_date.day+1):
			reconciliation_details = {}
			reconciliation_details["date"]=current_date
			reconciliation_details["day"]=get_weekday(current_date)
			current_date = add_to_date(current_date, days=1)
			reconciliation_data.append(reconciliation_details)

		holiday_list = frappe.db.get_all("Holiday List",
								   filters={"from_date":["<=",self.date],"to_date":[">=",self.date]},
								   fields=["name"])
		
		weekly_off_days = []
		if len(holiday_list)>0:
			get_weekly_off_list = frappe.db.get_all("Holiday",
											parent_doctype="Holiday List",
											filters={"parent":holiday_list[0].name,"weekly_off":1},
											fields=["description"],
											group_by="description",debug=1)

			if len(get_weekly_off_list)>0:
				for row in get_weekly_off_list:
					weekly_off_days.append(row.description)

		get_attendance = frappe.db.get_all("Attendance",
									 filters={"employee":self.employee_no,"attendance_date":["between",[month_start_date,month_end_date]]},
									 fields=["name","attendance_date","custom_attendance_type","custom_actual_delay_minutes","custom_actual_early_minutes","status","late_entry","early_exit"])
		
		for row in reconciliation_data:
			for day in weekly_off_days:
				if row.get("day") == day:
					row["type"]="Weekly Off"

			if row.get("day") not in weekly_off_days:
				if len(get_attendance)>0:
					for attendance in get_attendance:
						if row.get("date") == attendance.attendance_date:
							row["type"]=attendance.attendance_type
							row["delay_in"]=attendance.custom_actual_delay_minutes
							row["early_out"]=attendance.custom_actual_early_minutes
							row["attendance_reference"]=attendance.name
		return reconciliation_data

