# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import month_diff, today, flt, getdate, add_to_date
from frappe.model.document import Document


class EducationAllowanceRequestST(Document):
	
	def validate(self):
		self.set_season_type_based_on_date()
		self.validate_employee_not_in_test_period()
		self.claculate_and_validate_child_and_age()
		self.calculate_and_validate_approved_amount()
		self.calculate_unpaid_amount()
		self.validate_duplicate_record()

	def validate_duplicate_record(self):
		exist_request = frappe.db.exists("Education Allowance Request ST", {"name":["!=",self.name],"employee_no":self.employee_no,"educational_year":self.educational_year,"season_type":self.season_type})
		if exist_request != None:
			frappe.throw(_("You cannot create request again for same Educational year and Season"))

	def set_season_type_based_on_date(self):
		stats_settings_doc = frappe.get_doc("Stats Settings ST","Stats Settings ST")
		print(self.creation_date, "---self.creation_date---", type(self.creation_date))
		print(stats_settings_doc.first_season_apply_start_date, "---stats_settings_doc.first_season_apply_start_date---", type(stats_settings_doc.first_season_apply_start_date))
		creation_date = getdate(self.creation_date)
		if (creation_date.month == getdate(stats_settings_doc.first_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.first_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.first_season_apply_end_date).day):
			self.season_type = "First Season"
		elif (creation_date.month == getdate(stats_settings_doc.second_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.second_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.second_season_apply_end_date).day):
			self.season_type = "Second Season"
		elif (creation_date.month == getdate(stats_settings_doc.third_season_apply_start_date).month) and (
			creation_date.day >= getdate(stats_settings_doc.third_season_apply_start_date).day or 
			creation_date.day <= getdate(stats_settings_doc.third_season_apply_end_date).day):
			self.season_type = "Third Season"
		
		if self.season_type == None or self.season_type == "":
			frappe.throw(_("You cannot apply for education allowance on {0}.<br>It does not belongs to any season.".format(self.creation_date)))
		
	def validate_employee_not_in_test_period(self):
		employee_joining_date = frappe.db.get_value("Employee",self.employee_no,"date_of_joining")
		test_period = add_to_date(getdate(employee_joining_date), months=6)
		if test_period > getdate(self.creation_date): 
				frappe.throw(_("Employee is in test period<br>Hence cannot apply for Education Allowance"))

	def claculate_and_validate_child_and_age(self):
		if len(self.education_allowance_request_details)>0:
			if len(self.education_allowance_request_details)>3:
				frappe.throw(_("Maximum 3 children are allowed for Education Allowance."))
			for row in self.education_allowance_request_details:
				if row.date_of_birth:
					child_age = (month_diff(today(),row.date_of_birth))/12
					print(child_age,"======",child_age/12)
					row.age = child_age
					min_allowed_age, max_allowed_age = frappe.db.get_value("Stats Settings ST",None,["minimum_age_for_education_allowance","maximum_age_for_education_allowance"])
					print(min_allowed_age, max_allowed_age,"----")
					if child_age < flt(min_allowed_age) or child_age > flt(max_allowed_age):
						frappe.throw(_("#Row {0} :{1} is not eligible for Education Allowance".format(row.idx,row.child_name)))

	def calculate_and_validate_approved_amount(self):
		total_approved_amount = 0
		check_against_grade_limit = frappe.db.get_single_value("Stats Settings ST","check_against_grade_limit")
		print(check_against_grade_limit,"---Stats Settings ST")
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				if check_against_grade_limit == 1:
					limit_per_season = self.limit / 3
					if row.approved_amount > limit_per_season:
						frappe.throw(_("#Row {0} :Your approved amount cannot be greater than {1}".format(row.idx,flt(limit_per_season,2))))
				total_approved_amount = total_approved_amount + row.approved_amount
		
		self.approved_amount = total_approved_amount

	def calculate_unpaid_amount(self):
		previous_allowance_requests = frappe.db.get_all("Education Allowance Request ST",
												  filters={"employee_no":self.employee_no,"educational_year":self.educational_year,"docstatus":1},
												  fields=["name"])
		
		if len(self.education_allowance_request_details)>0:
			for row in self.education_allowance_request_details:
				previous_unpaid = 0
				diff_of_requested_approved = row.requested_amount - row.approved_amount
				if diff_of_requested_approved >= 0:
					row.present_unpaid = diff_of_requested_approved
				if len(previous_allowance_requests)>0:
					for request in previous_allowance_requests:
						if request.name != self.name:
							unpaid = frappe.db.get_value("Education Allowance Request Details ST",{"parent":request.name,"child_name":row.child_name},"present_unpaid")
							print(unpaid,"unpaid")
							previous_unpaid = previous_unpaid + (unpaid or 0)
					row.previous_unpaid = previous_unpaid
					if diff_of_requested_approved < 0:
						row.total_unpaid = (row.present_unpaid or 0) + previous_unpaid + diff_of_requested_approved
					else :
						row.total_unpaid = (row.present_unpaid or 0) + previous_unpaid
				else:
					row.total_unpaid = row.present_unpaid

	@frappe.whitelist()
	def get_employee_dependants(self):
		employee_family_details = []
		employee_doc = frappe.get_doc("Employee", self.employee_no)
		if len(employee_doc.custom_dependants)>0:
			for row in employee_doc.custom_dependants:
				employee_child = {}
				if row.relation in ["Son","Daughter"]:
					employee_child["name"]=row.name1
					employee_child["relation"]=row.relation
					employee_child["date_of_birth"]=row.date_of_birth
					employee_family_details.append(employee_child)
		print(employee_family_details,"--------family details")
		return employee_family_details