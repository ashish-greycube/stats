# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class BusinessTripSheetST(Document):
	def on_submit(self):
		if len(self.employee_detail)>0:
			for row in self.employee_detail:
				frappe.db.set_value("Employee Task Completion ST",row.employee_task_completion_reference,"process_status","Processed")
				frappe.msgprint(_("Process status of {0} is changed to {1}").format(get_link_to_form("Employee Task Completion ST", row.employee_task_completion_reference),"Processed"),alert=1)
