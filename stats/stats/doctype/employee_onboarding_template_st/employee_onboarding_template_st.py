# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeOnboardingTemplateST(Document):
	def validate(self):
		self.validate_company_email_creation_task()

	def validate_company_email_creation_task(self):
		if len(self.activities) > 0:
			for act1 in self.activities:
				if act1.company_email_creation_task == 1:
					for act2 in self.activities:
						if act2.company_email_creation_task == 1 and act2.name != act1.name:
							frappe.throw(_("Company Email Creation Task Should be one time only."))
