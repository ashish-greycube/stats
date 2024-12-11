# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationalYearST(Document):
	
	def validate(self):
		self.validate_from_to_year()

	def validate_from_to_year(self):
		if self.educational_year_from > self.educational_year_to:
			frappe.throw(_("From Year cannot be greater than To year"))