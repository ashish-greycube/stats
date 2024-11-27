# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ResignationTypeST(Document):
	def validate(self):
		self.validate_resignation_type()

	def validate_resignation_type(self):
		if ((self.is_it_separation == 1 and (self.is_it_not_renewal_of_contract == 1 or self.is_it_resignation == 1)) or 
			(self.is_it_resignation == 1 and (self.is_it_separation == 1 or self.is_it_not_renewal_of_contract == 1)) or 
			(self.is_it_not_renewal_of_contract == 1 and (self.is_it_resignation == 1 or self.is_it_separation))):
			frappe.throw(_("You Cann't Check Multiple Resignation Type"))
