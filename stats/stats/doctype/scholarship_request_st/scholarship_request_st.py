# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ScholarshipRequestST(Document):
	def validate(self):
		self.validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type()

	def validate_duplicate_entry_based_on_employee_scholarship_and_specialisation_type(self):
		scholarship_list = frappe.db.get_all
		exists_scholarship = frappe.db.exists("Scholarship Request ST", {"employee_no": self.employee_no,"scholarship_no": self.scholarship_no,"specialisation_type": self.specialisation_type})
		print(exists_scholarship,self.employee_no,self.scholarship_no,self.specialisation_type,self.name,"--------------------")
		if exists_scholarship != None and exists_scholarship != self.name:
			frappe.throw(_("You cannot create Scholarship Request for same employee, scholarship no and specification type."))

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


