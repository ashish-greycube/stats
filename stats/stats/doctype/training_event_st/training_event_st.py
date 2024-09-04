# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class TrainingEventST(Document):
	def on_submit(self):
		if self.training_status == "Closed":
			if len(self.training_event_employee_details)>0:
				for row in self.training_event_employee_details:
					frappe.db.set_value("Training Request ST",row.training_request_reference,"status","Finished")
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),"Finished"),alert=1)
					create_training_evaluation(self.name,row.employee_no)
					frappe.db.set_value("Training Event ST",self.name,"training_status","Finished")
		

	@frappe.whitelist()
	def fetch_training_request(self):
		approved_training_request_list = frappe.db.get_all("Training Request ST",
													 filters = {"training_event":self.name,"docstatus":1,"status":"Accepted"},
													 fields=["name"])
		return approved_training_request_list

def create_training_evaluation(training_event,employee):
		training_evaluation_doc = frappe.new_doc("Training Evaluation ST")
		training_evaluation_doc.employee_no = employee
		training_evaluation_doc.training_event = training_event
		training_evaluation_doc.run_method("set_missing_values")
		training_evaluation_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Training Evaluation is created {0}").format(get_link_to_form("Training Evaluation ST",training_evaluation_doc.name)),alert=True)
		return training_evaluation_doc.name