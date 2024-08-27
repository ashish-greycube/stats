# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,today,date_diff


class BusinessTripProcessingST(Document):
	def validate(self):
		self.calculate_no_of_days_for_multi_direction()
		self.set_created_by()

	def on_submit(self):
		if len(self.business_trip_detail)>0:
			for row in self.business_trip_detail:
				if row.action == "Pending":
					frappe.throw(_("You cannot submit.<br>Please Approve or Reject Business trip request {0} in row {1}").format(row.business_trip_reference,row.idx))
					
		self.change_btr_status()
		self.change_btp_status()
		self.update_no_of_trip_days_remaining()

	def change_btr_status(self):
		if len(self.get("business_trip_detail")) > 0:
			for item in self.get("business_trip_detail"):
				btr_doc = frappe.get_doc("Business Trip Request ST",item.business_trip_reference)
				if btr_doc.status != item.action:
					btr_doc.status = item.action
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Business Trip Request ST", btr_doc.name),item.action),alert=1)
					if item.action == "Approved":
						btr_doc.date_of_approval = today()
					btr_doc.save(ignore_permissions=True)
	
	def change_btp_status(self):
		if len(self.get("business_trip_detail")) > 0:
			for item in self.get("business_trip_detail"):
				if item.action == "Pending":
					self.status = "Pending"
					status = "Pending"
					return
				else :
					self.status = "Processed"
					status = "Processed"
			if status == "Processed":
				frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Business Trip Processing ST", self.name),self.status),alert=1)

	def calculate_no_of_days_for_multi_direction(self):
		if len(self.get("business_trip_multi_direction_detail"))>0:
			for row in self.get("business_trip_multi_direction_detail"):
				if row.from_date and row.to_date:
					self.no_of_days = date_diff(row.to_date, row.from_date)

	def set_created_by(self):
		if not self.created_by_employee:
			emp=frappe.get_doc('Employee',{'user_id': frappe.session.user})
			if emp:
				self.created_by_employee=emp.employee_name
				self.created_by_sub_department=emp.custom_sub_department

	def update_no_of_trip_days_remaining(self):
		if len(self.get("business_trip_detail"))>0:
			for row in self.get("business_trip_detail"):
				if row.action == "Approved":
					print("----"*100)
					btr_doc_emp = frappe.db.get_value("Business Trip Request ST",row.business_trip_reference,"employee_no")
					custom_no_of_business_trip_days_remaining = frappe.db.get_value("Employee",btr_doc_emp,"custom_no_of_business_trip_days_remaining")
					current_remaining_trip_days = custom_no_of_business_trip_days_remaining - row.no_of_days
					frappe.db.set_value("Employee",btr_doc_emp,"custom_no_of_business_trip_days_remaining",current_remaining_trip_days)


@frappe.whitelist()
def fetch_business_trip_request(name):
	main_department, sub_department, from_date, to_date = frappe.db.get_value("Business Trip Processing ST",name,["main_department","sub_department","from_date","to_date"])
	btr_list = frappe.db.get_all("Business Trip Request ST",
							  filters={"docstatus":1,"status":"Pending","main_department":main_department,"sub_department":sub_department,"creation_date":["between",[from_date,to_date]]},
							  fields=["name"])
	return btr_list
