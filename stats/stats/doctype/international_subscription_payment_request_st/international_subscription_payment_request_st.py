# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class InternationalSubscriptionPaymentRequestST(Document):
	
	@frappe.whitelist()
	def create_achievement_certificate(self):
		certificate_doc = frappe.new_doc("Achievement Certificate ST")
		certificate_doc.request_reference = self.name
		certificate_doc.run_method("set_missing_values")
		certificate_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Achievement Certificate is created {0}".format(get_link_to_form("Achievement Certificate ST",certificate_doc.name))),alert=True)

		return certificate_doc.name