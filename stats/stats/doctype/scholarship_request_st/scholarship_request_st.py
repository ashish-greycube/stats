# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_to_date, get_datetime, get_date_str, cstr, get_first_day, get_last_day, getdate, time_diff_in_hours
from stats.hr_utils import check_if_holiday_between_applied_dates

class ScholarshipRequestST(Document):
	def validate(self):
		self.validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type()
		# self.validate_maximum_applications()
		# self.create_salary_structure_for_start_date_of_month()
		# self.create_salary_structure_for_other_than_start_date_of_month()
		# self.create_additional_salary_structure()

	def on_update_after_submit(self):
		self.create_salary_structure_for_start_date_of_month()
		self.create_salary_structure_for_other_than_start_date_of_month()
		# self.create_additional_salary_structure()
		# self.create_future_attendance_for_scholarship_time()

	def validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type(self):
		exists_scholarship = frappe.db.exists("Scholarship Request ST", {"employee_no": self.employee_no,"scholarship_no": self.scholarship_no,"specialisation_type": self.specialisation_type})
		print(exists_scholarship,self.employee_no,self.scholarship_no,self.specialisation_type,self.name,"--------------------")
		if exists_scholarship != None and exists_scholarship != self.name:
			frappe.throw(_("You cannot create Scholarship Request for same employee, scholarship no and specification type."))

	def create_future_attendance_for_scholarship_time(self):
		if self.acceptance_status == "Accepted":
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

				check_holiday = None
				for ele in yearly_holiday_list:
					if attendance_date.year == ele.get("year"):
						check_holiday = check_if_holiday_between_applied_dates(self.employee_no,attendance_date,attendance_date,holiday_list=ele.get("holiday_list"))

				if check_holiday == False:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.employee_no
					attendance_doc.attendance_date = attendance_date
					attendance_doc.custom_attendance_type = "Scholarship"

					employee_shift = frappe.db.get_value("Employee",self.employee_no,"default_shift")
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
				else :
					pass

			frappe.msgprint(_("Attendance from {0} to {1} is created.").format(self.scholarship_start_date,self.scholarship_end_date),alert=True)

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
												fields=["qualification","english_required"])
			return scholarship_details_list
		
	def create_salary_structure_for_start_date_of_month(self):
		if self.docstatus == 1:
			if self.acceptance_status == "Accepted" and self.scholarship_start_date:

				future_salary_assignment = frappe.db.get_all("Salary Structure Assignment",
												 fields=["name"],
												 filters={"from_date": [">=", self.scholarship_start_date],
					  									"employee": self.employee_no, "docstatus":1}, limit=1)
				print(future_salary_assignment, '--future_salary_assignment')
				if len(future_salary_assignment) > 0:
					doc = frappe.get_doc("Salary Structure Assignment", future_salary_assignment[0].name)
					doc.cancel() 
					frappe.msgprint(_("Salary Structure Assignment {0} Cancelled.").format(future_salary_assignment[0].name),alert=1)

				print("*******************************")
				latest_salary_structure = frappe.db.get_all("Salary Structure", 
												fields=["custom_employee_no", "name"],
												filters={"custom_employee_no": self.employee_no, "docstatus":1}, limit=1)
				print(latest_salary_structure, '---latest_salary_structure')
				if len(latest_salary_structure) > 0:
					prev_ss = frappe.get_doc("Salary Structure", latest_salary_structure[0].name)
					# print(get_first_day(self.scholarship_start_date)== getdate(self.scholarship_start_date),'-----get_first_day(self.scholarship_start_date)s')
					if get_first_day(self.scholarship_start_date) == getdate(self.scholarship_start_date):

						new_ss = frappe.copy_doc(prev_ss)
						new_ss.__newname = self.employee_no + "/" + self.name
						new_ss.name = self.employee_no + "/" + self.name
						new_ss.custom_contract_start_date = self.scholarship_start_date

						basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

						if basic_salary_component == None:
							frappe.throw(_("Set Basic Salary Component in Stats Settings"))

						basic_ear = 0
						for row in prev_ss.earnings:
							if row.salary_component == basic_salary_component :
								basic_ear = row.amount
								break

						new_ss.earnings = []
						# new_ss.deductions = []
						ear = new_ss.append("earnings", {})
						ear.salary_component = basic_salary_component
						ear.amount = basic_ear * 0.5
						ear.amount_based_on_formula = 0
						ear.is_tax_applicable = 0

						new_ss.save(ignore_permissions=True)

						frappe.msgprint(_("Salary Structure {0} created.").format(new_ss.name), alert=1)

						new_ss.submit()
					
					######### create salary structure assignment

					if get_last_day(self.scholarship_end_date) == getdate(self.scholarship_end_date):
						if self.scholarship_end_date:
							total_monthly_salary = 0
							if len(prev_ss.earnings)>0:
								for ear in prev_ss.earnings:
									total_monthly_salary = total_monthly_salary + ear.amount

							next_month = add_to_date(self.scholarship_end_date,months=1)
							assignment = frappe.new_doc("Salary Structure Assignment")
							assignment.employee = self.employee_no
							assignment.salary_structure = prev_ss.name
							assignment.from_date = get_first_day(next_month)
							assignment.base = total_monthly_salary

							assignment.save(ignore_permissions=True)
							frappe.msgprint(_("Salary Structure Assignment {0} created." .format(assignment.name)), alert=True)
							assignment.submit()

	def create_additional_salary_structure(self):
		if self.docstatus == 1:
			if self.acceptance_status == "Accepted" and self.scholarship_start_date:
				latest_salary_structure = frappe.db.get_all("Salary Structure", 
												fields=["custom_employee_no", "name"],
												filters={"custom_employee_no": self.employee_no, "docstatus":1}, limit=1)
				
				if len(latest_salary_structure) > 0:
					if get_first_day(self.scholarship_start_date) != self.scholarship_start_date:
						prev_ss = frappe.get_doc("Salary Structure", latest_salary_structure[0].name)
						for ear in prev_ss.earnings:
							additional_salary = frappe.new_doc('Additional Salary')
							additional_salary.employee = self.employee_no
							additional_salary.payroll_date = self.scholarship_start_date
							additional_salary.salary_component =  ear.salary_component
							additional_salary.overwrite_salary_structure_amount = 1

							basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

							if basic_salary_component == None:
								frappe.throw(_("Set Basic Salary Component in Stats Settings"))

							before_scholarship_days = (getdate(self.scholarship_start_date).day - 1)
							if ear.salary_component == basic_salary_component:
								end_date = get_last_day(self.scholarship_start_date).day - before_scholarship_days
								salary_before_scholarship = (before_scholarship_days * ear.amount) / 30
								salary_scholarship = (end_date * 0.5 * ear.amount) / 30
								additional_salary.amount = salary_before_scholarship + salary_scholarship
							else:
								additional_salary.amount = (before_scholarship_days * ear.amount) / 30

							additional_salary.save(ignore_permissions=True)
							frappe.msgprint(_("Additional Salary {0} Created").format(additional_salary.name), alert=1)

						# for ded in prev_ss.deductions:
						# 	additional_ded = frappe.new_doc('Additional Salary')
						# 	additional_ded.employee = self.employee_no
						# 	additional_ded.payroll_date = self.scholarship_start_date
						# 	additional_ded.salary_component = ded.salary_component
						# 	additional_ded.overwrite_salary_structure_amount = 1
						# 	additional_ded.amount = "will do calculation"

						# 	additional_ded.save(ignore_permissions=True)

	def create_salary_structure_for_other_than_start_date_of_month(self):
		if self.docstatus == 1:
			if self.acceptance_status == "Accepted" and self.scholarship_start_date:
				latest_salary_structure = frappe.db.get_all("Salary Structure", 
												fields=["custom_employee_no", "name"],
												filters={"custom_employee_no": self.employee_no, "docstatus":1}, limit=1)
				
				if len(latest_salary_structure) > 0:
					prev_ss = frappe.get_doc("Salary Structure", latest_salary_structure[0].name)
					# print(get_first_day(self.scholarship_start_date), '-----get_first_day(self.scholarship_start_date)s')
					if get_first_day(self.scholarship_start_date) != getdate(self.scholarship_start_date):

						######### additonal salary for scholarship starting month
						for ear in prev_ss.earnings:
							additional_salary = frappe.new_doc('Additional Salary')
							additional_salary.employee = self.employee_no
							additional_salary.payroll_date = self.scholarship_start_date
							additional_salary.salary_component =  ear.salary_component
							additional_salary.overwrite_salary_structure_amount = 1

							basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

							if basic_salary_component == None:
								frappe.throw(_("Set Basic Salary Component in Stats Settings"))

							before_scholarship_days = (getdate(self.scholarship_start_date).day - 1)
							if ear.salary_component == basic_salary_component:
								end_date = get_last_day(self.scholarship_start_date).day - before_scholarship_days
								salary_before_scholarship = (before_scholarship_days * ear.amount) / 30
								salary_scholarship = (end_date * 0.5 * ear.amount) / 30
								additional_salary.amount = salary_before_scholarship + salary_scholarship
							else:
								additional_salary.amount = (before_scholarship_days * ear.amount) / 30

							additional_salary.save(ignore_permissions=True)
							frappe.msgprint(_("Additional Salary {0} Created").format(additional_salary.name), alert=1)
							additional_salary.submit()

						######### new salary structure for next month
						next_month_date = add_to_date(self.scholarship_start_date,months=1)

						new_ss = frappe.copy_doc(prev_ss)
						new_ss.__newname = self.employee_no + "/" + self.name
						new_ss.name = self.employee_no + "/" + self.name
						new_ss.custom_contract_start_date = get_first_day(next_month_date)

						basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')

						basic_ear = 0
						for row in prev_ss.earnings:
							if row.salary_component == basic_salary_component :
								basic_ear = row.amount

						new_ss.earnings = []
						# new_ss.deductions = []
						earning = new_ss.append("earnings", {})
						earning.salary_component = basic_salary_component
						earning.amount = basic_ear * 0.5
						earning.amount_based_on_formula = 0
						earning.is_tax_applicable = 0

						new_ss.save(ignore_permissions=True)
						frappe.msgprint(_("Salary Structure {0} created.").format(new_ss.name), alert=1)
						new_ss.submit()


					if get_last_day(self.scholarship_end_date) != getdate(self.scholarship_end_date):

						######### additonal salary for scholarship ending month
						for ear in prev_ss.earnings:
							additional_salary = frappe.new_doc('Additional Salary')
							additional_salary.employee = self.employee_no
							additional_salary.payroll_date = self.scholarship_end_date
							additional_salary.salary_component =  ear.salary_component
							additional_salary.overwrite_salary_structure_amount = 1

							basic_salary_component = frappe.db.get_single_value('Stats Settings ST', 'basic_salary_component')
							if basic_salary_component == None:
								frappe.throw(_("Set Basic Salary Component in Stats Settings"))

							after_scholarship_days = (30 - getdate(self.scholarship_end_date).day)
							if ear.salary_component == basic_salary_component:
								scholarship_days = getdate(self.scholarship_end_date).day
								salary_scholarship = (scholarship_days * 0.5 * ear.amount) / 30
								salary_after_scholarship = (after_scholarship_days * ear.amount) / 30
								additional_salary.amount = salary_after_scholarship + salary_scholarship
							else:
								additional_salary.amount = (after_scholarship_days * ear.amount) / 30

							additional_salary.save(ignore_permissions=True)
							frappe.msgprint(_("Additional Salary {0} Created").format(additional_salary.name), alert=1)
							additional_salary.submit()

						######### create salary structure assignment form next month

						if self.scholarship_end_date:
							total_monthly_salary = 0
							if len(prev_ss.earnings)>0:
								for ear in prev_ss.earnings:
									total_monthly_salary = total_monthly_salary + ear.amount

							scholarship_end_next_month = add_to_date(self.scholarship_end_date,months=1)
							assignment = frappe.new_doc("Salary Structure Assignment")
							assignment.employee = self.employee_no
							assignment.salary_structure = prev_ss.name
							assignment.from_date = get_first_day(scholarship_end_next_month)
							assignment.base = total_monthly_salary

							assignment.save(ignore_permissions=True)
							frappe.msgprint(_("Salary Structure Assignment {0} created." .format(assignment.name)), alert=True)
							assignment.submit()


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


