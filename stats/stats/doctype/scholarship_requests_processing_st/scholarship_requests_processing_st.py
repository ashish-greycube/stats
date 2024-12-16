# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, date_diff, add_to_date, get_datetime, get_date_str, cstr, time_diff_in_hours
from stats.hr_utils import check_if_holiday_between_applied_dates


class ScholarshipRequestsProcessingST(Document):
	def on_submit(self):
		if len(self.scholarship_request_details)>0:
			for row in self.scholarship_request_details:
				if row.action == "Open":
					frappe.throw(_("You cannot submit.<br>Please Accept or Reject Scholarship Request {0} in row {1}").format(row.scholarship_request_reference,row.idx))
				
		self.change_scholarship_request_status()
		self.create_future_attendance_for_scholarship_time()

	def change_scholarship_request_status(self):
		if len(self.get("scholarship_request_details")) > 0:
			for item in self.get("scholarship_request_details"):
				scholarship_request_doc = frappe.get_doc("Scholarship Request ST",item.scholarship_request_reference)
				if scholarship_request_doc.acceptance_status != item.action:
					scholarship_request_doc.acceptance_status = item.action
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Scholarship Request ST", scholarship_request_doc.name),item.action),alert=1)
					scholarship_request_doc.save(ignore_permissions=True)

	def create_future_attendance_for_scholarship_time(self):
		if len(self.scholarship_request_details)> 0:
			days = date_diff(self.scholarship_end_date,self.scholarship_start_date)
			
			different_years_list = []
			for fiscal_year in range ((self.scholarship_start_date).year, (self.scholarship_end_date).year+1):
				if fiscal_year not in different_years_list:
					different_years_list.append(fiscal_year)

			yearly_holiday_list = []

			for year in different_years_list:
				holiday = {}
				fiscal_year_doc = frappe.get_doc("Fiscal Year",year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"])
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot create future attendance.").format(year))
				else :
					holiday["year"]=year
					holiday["holiday_list"]=exist_holiday_list[0].name
					yearly_holiday_list.append(holiday)

			for day in range (days+1):
				attendance_date = add_to_date(self.scholarship_start_date,days=day)
				
				for row in self.scholarship_request_details:
					if row.action == "Accepted":
						check_holiday = None
						for ele in yearly_holiday_list:
							if attendance_date.year == ele.get("year"):
								check_holiday = check_if_holiday_between_applied_dates(row.employee_no,attendance_date,attendance_date,holiday_list=ele.get("holiday_list"))
						
						if check_holiday == False:
							attendance_doc = frappe.new_doc("Attendance")
							attendance_doc.employee = row.employee_no
							attendance_doc.attendance_date = attendance_date
							attendance_doc.custom_attendance_type = "Scholarship"

							employee_shift = frappe.db.get_value("Employee",row.employee_no,"default_shift")
							shift_start_time = frappe.db.get_value("Shift Type",employee_shift,"start_time")
							shift_end_time = frappe.db.get_value("Shift Type",employee_shift,"end_time")

							in_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_start_time))
							out_time = get_datetime(get_date_str(attendance_date) + " " + cstr(shift_end_time))
							total_working_hours = time_diff_in_hours(in_time, out_time)

							attendance_doc.shift = employee_shift
							attendance_doc.in_time = in_time
							attendance_doc.out_time = out_time
							attendance_doc.working_hours = total_working_hours
							attendance_doc.status = "Present"
							attendance_doc.save(ignore_permissions=True)
							attendance_doc.submit()

			frappe.msgprint(_("Attendance from {0} to {1} is created.").format(self.scholarship_start_date,self.scholarship_end_date),alert=True)

	@frappe.whitelist()
	def get_scholarship_requests(self):
			
		filters={"docstatus":1,"acceptance_status": "Open","scholarship_no":self.scholarship_no}

		if self.from_date and self.to_date:
			filters["transaction_date"]=["between", [self.from_date, self.to_date]]
		if self.main_department:
			filters["main_department"]=self.main_department
		if self.sub_department:
			filters["sub_department"]=self.sub_department
		if self.specialisation_type:
			filters["specialisation_type"]=self.specialisation_type

		scholarship_request_list = frappe.db.get_all('Scholarship Request ST', filters=filters,fields=["name"],debug=1)

		if len(scholarship_request_list) < 1:
			frappe.msgprint(_("No data found"))

		return scholarship_request_list




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_open_scholarships(doctype, txt, searchfield, start, page_len, filters):
	open_scholarships = frappe.db.get_all("Scholarship ST",
									   filters={"docstatus":1,"status":"Open"},
									   fields=["scholarship_no"],as_list=1)
	return open_scholarships


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_specialisation_type_from_scholarship_no(doctype, txt, searchfield, start, page_len, filters):
	scholarship_no = filters.get("scholarship_no")
	scholarship_doc = frappe.get_doc("Scholarship ST",{"scholarship_no":scholarship_no})
	specialisation_type_list = frappe.db.get_all("Scholarship Details ST",
									   parent_doctype = "Scholarship ST",
									   filters={"parent":scholarship_doc.name},
									   fields=["specialisation_type"],as_list=1)
	return specialisation_type_list