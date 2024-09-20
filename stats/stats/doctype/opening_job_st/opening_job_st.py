# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OpeningJobST(Document):
	pass


@frappe.whitelist()
def get_job_deatils(job_title):
	job_deatils = frappe.db.get_value('MP Jobs Details ST', job_title, 
								   ['designation', 'main_job_department', 'sub_job_department', 'grade', 'section', 'salary', 'branch', 'employment_type', 'contract_type'], as_dict=1)
	return job_deatils