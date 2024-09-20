# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EmployeeOnboardingST(Document):
	def on_submit(self):
		self.create_todo()

	def create_todo(self):
		for op in self.onboarding_procedures:
			if not op.todo:

				todo = frappe.new_doc('ToDo')
				todo.description = op.activity_name
				todo.custom_candidate_name = self.candidate_name
				todo.custom_candidate_namein_english = self.candidate_namein_english
				todo.custom_email = self.email
				todo.custom_phone_no = self.phone_no
				todo.reference_type = self.doctype
				todo.reference_name = self.name

				if op.company_email_creation_task == 1:
					todo.custom_create_company_email_for_employee = 1

				todo.run_method("set_missing_values")
				todo.save(ignore_permissions=True)

				frappe.db.set_value('Onboarding Procedures ST', op.name, 'todo', todo.name)
				frappe.msgprint(_("ToDo List Created: {0}").format(todo.name), alert=1)

@frappe.whitelist()
def get_onboarding_details(parent, parenttype):

	return frappe.get_all(
		"Employee Boarding Activity ST",
		fields=[
			"activity_name",
			"user",
			"full_name",
			"company_email_creation_task"
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)
