# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeOnboardingST(Document):
	pass

@frappe.whitelist()
def get_onboarding_details(parent, parenttype):

	return frappe.get_all(
		"Employee Boarding Activity ST",
		fields=[
			"activity_name",
			"user",
			"full_name",
		],
		filters={"parent": parent, "parenttype": parenttype},
		order_by="idx",
	)
