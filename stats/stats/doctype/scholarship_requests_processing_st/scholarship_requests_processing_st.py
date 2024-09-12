# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class ScholarshipRequestsProcessingST(Document):
	def on_submit(self):
		if len(self.scholarship_request_details)>0:
			for row in self.scholarship_request_details:
				if row.action == "Open":
					frappe.throw(_("You cannot submit.<br>Please Accept or Reject Scholarship Request {0} in row {1}").format(row.scholarship_request_reference,row.idx))
				
		self.change_scholarship_request_status()

	def change_scholarship_request_status(self):
		if len(self.get("scholarship_request_details")) > 0:
			for item in self.get("scholarship_request_details"):
				scholarship_request_doc = frappe.get_doc("Scholarship Request ST",item.scholarship_request_reference)
				if scholarship_request_doc.acceptance_status != item.action:
					scholarship_request_doc.acceptance_status = item.action
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Scholarship Request ST", scholarship_request_doc.name),item.action),alert=1)
					scholarship_request_doc.save(ignore_permissions=True)


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