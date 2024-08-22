# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ManPowerPlanChangeRequestST(Document):
	def on_submit(self):
		self.change_pervious_job_details()
		self.create_new_job_details()

	def change_pervious_job_details(self):
		if self.request_type == "Update Existing Job":
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'designation', self.designation_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'main_job_department', self.main_department_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'sub_job_department', self.sub_department_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'grade', self.grade_cp)
			frappe.db.set_value('MP Jobs Details ST',self.job_no, 'salary', self.salary_cp)

			frappe.msgprint(_("Update Job No. {0} Details in Man Power Planning {1}").format(self.job_no, self.man_power_planning_reference), alert=1)
			

	def create_new_job_details(self):
		if self.request_type == "New Job":
			if frappe.db.exists('MP Jobs Details ST', self.new_job_no):
				frappe.throw(_("{0} Job No deatils are already exist, Please create new jon no.").format(self.new_job_no))
				return
			
			man_power = frappe.get_doc('Man Power Planning ST', self.man_power_planning_reference)
			row = man_power.append("job_details")
			row.job_no = self.new_job_no
			row.designation = self.designation_nj
			row.main_job_department = self.main_department_nj
			row.sub_job_department = self.sub_department_nj
			row.grade = self.grade_np
			row.salary = self.salary_nj

			man_power.save(ignore_permissions=True)

			frappe.msgprint(_("Add New Job No. {0} in Man Power Planning {1}").format(self.job_no, self.man_power_planning_reference), alert=1)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_job_no(doctype, txt, searchfield, start, page_len, filters):
		
		parent = filters.get('parent')
		job_details = frappe.get_all("MP Jobs Details ST", filters={"parent":parent}, fields=["name"], as_list=1)
		job_no = tuple(set(job_details))
		# print(unique, '----------ab')
		return job_no