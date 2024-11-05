# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr
from stats.hr_utils import check_if_holiday_between_applied_dates


class ScholarshipRequestST(Document):
	def validate(self):
		self.validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type()
		self.validate_maximum_applications()

	def validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type(self):
		exists_scholarship = frappe.db.exists("Scholarship Request ST", {"employee_no": self.employee_no,"scholarship_no": self.scholarship_no,"specialisation_type": self.specialisation_type})
		print(exists_scholarship,self.employee_no,self.scholarship_no,self.specialisation_type,self.name,"--------------------")
		if exists_scholarship != None and exists_scholarship != self.name:
			frappe.throw(_("You cannot create Scholarship Request for same employee, scholarship no and specification type."))
		
	def on_update_after_submit(self):
		self.create_future_attendance_for_scholarship_time()

	def create_future_attendance_for_scholarship_time(self):
		if self.acceptance_status == "Accepted":
			days = date_diff(self.scholarship_end_date,self.scholarship_start_date)
			print(days)
			for day in range (days+1):
				attendance_date = add_to_date(self.scholarship_start_date,days=day)
				check_holiday = check_if_holiday_between_applied_dates(self.employee_no,attendance_date,attendance_date)
				print(check_holiday,"------")
				if check_holiday == False:
					print("****************")
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.employee_no
					attendance_doc.attendance_date = attendance_date
					attendance_doc.custom_attendance_type = "Scholarship"
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
				else:
					pass

	def validate_maximum_applications(self):
		if self.scholarship_no and self.specialisation_type:
			scholarship = frappe.db.get_all("Scholarship ST",filters={"scholarship_no":self.scholarship_no},fields=["name"])
			if len(scholarship)>0:
				scholarship_doc = frappe.get_doc("Scholarship ST",scholarship[0].name)
				for row in scholarship_doc.scholarship_details:
					if row.specialisation_type == self.specialisation_type:
						maximum_applicants = row.max_no_of_applicants
				scholarship_requests_list = frappe.db.get_all("Scholarship Request ST",
												  filters={"scholarship_no":self.scholarship_no,"specialisation_type":self.specialisation_type},
												  fields=["name"])
				print(len(scholarship_requests_list),"len(scholarship_requests_list)",maximum_applicants,"maximum_applicants")
				if len(scholarship_requests_list) and len(scholarship_requests_list) > maximum_applicants:
					frappe.throw(_("You cannot apply for scholarship because maximum limit is {0}").format(maximum_applicants))

	@frappe.whitelist()
	def fetch_scholarship_details_based_on_specialisation_type(self):
		if self.specialisation_type:
			scholarship_doc = frappe.get_doc("Scholarship ST",{"scholarship_no":self.scholarship_no})
			scholarship_details_list = frappe.db.get_all("Scholarship Details ST",
												filters={"parent":scholarship_doc.name,"specialisation_type":self.specialisation_type},
												fields=["qualification","scholarship_start_date","scholarship_end_date","english_required"])
			return scholarship_details_list
		
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


