# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,today


class BusinessTripProcessingST(Document):
	def validate(self):
		self.change_btr_status()
		self.change_btp_status()

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

@frappe.whitelist()
def fetch_business_trip_request(name):
	main_department, sub_department, from_date, to_date = frappe.db.get_value("Business Trip Processing ST",name,["main_department","sub_department","from_date","to_date"])
	btr_list = frappe.db.get_all("Business Trip Request ST",
							  filters={"docstatus":1,"main_department":main_department,"sub_department":sub_department,"creation_date":["between",[from_date,to_date]]},
							  fields=["name"])
	return btr_list
