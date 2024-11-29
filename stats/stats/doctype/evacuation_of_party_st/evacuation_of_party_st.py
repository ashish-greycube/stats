# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class EvacuationofPartyST(Document):
	def on_submit(self):
		resignation_doc = frappe.get_doc("Employee Resignation ST", self.resignation_reference)
		resignation_doc.employee_evacuation_status = "Processed"
		frappe.msgprint(_("In Employee Resignation: {0} Employee Evacuation Status Set to 'Processed'.").format(self.resignation_reference), alert=1)
		resignation_doc.add_comment("Comment",text="Employee Evacuation Status Set to <b>Processed</b> due to {0}".format(get_link_to_form(self.doctype,self.name)))
		resignation_doc.save(ignore_permissions=True)