# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EndOfServiceSheetST(Document):
	
	@frappe.whitelist()
	def get_employee_details_for_end_of_service(self):
		list_emp = frappe.db.get_all("End of Service Calculation ST", filters={"creation_date":["Between", [self.from_date, self.to_date]]},
							   fields=["name", "employee", "total_monthly_salary", "end_of_service_due_amount"])
		
		return list_emp
