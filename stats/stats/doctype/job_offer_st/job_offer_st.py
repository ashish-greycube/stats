# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.model.mapper import get_mapped_doc

class JobOfferST(Document):
	pass


@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	doc = frappe.get_doc("Job Offer ST", source_name)
	# doc.validate_employee_creation()

	def set_missing_values(source, target):
		target.custom_job_offer_reference = source.name
		target.personal_email = source.email
		target.status = "Active"
		target.first_name = source.candidate_name
		target.department = source.main_department
		target.custom_sub_department = source.sub_department
		target.custom_contract_type = source.contract_type
		target.employment_type = source.employment_type
		target.custom_idresidency_number = source.id_igama_no
		target.custom_id_expiration_date = source.id_expiration_date
		target.cell_number = source.phone_no

	doc = get_mapped_doc(
		"Job Offer ST",
		source_name,
		{
			"Job Offer ST": {
				"doctype": "Employee",
				"field_map": {
					"first_name": "candidate_name",
					"employee_grade": "grade",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc