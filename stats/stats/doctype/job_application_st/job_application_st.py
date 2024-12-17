# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, cint

class JobApplicationST(Document):
	def validate(self):
		self.validate_national_id_no()

	def validate_national_id_no(self):
		if self.id_igama_no:
			national_id = cstr(self.id_igama_no)

			if len(national_id) != 10:
				frappe.throw(_("Iqama/National ID No Must Be 10 Digits"))
