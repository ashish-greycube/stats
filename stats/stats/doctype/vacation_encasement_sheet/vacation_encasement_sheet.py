# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VacationEncasementSheet(Document):

	@frappe.whitelist()
	def get_employee_details_for_vacation_encasement(self):
		vacation_encasement_list = []

		resignation_list = frappe.db.get_all("End of Service Calculation ST", filters={"creation_date":["Between", [self.from_date, self.to_date]],"docstatus":1},
							   fields=["name", "employee", "vacation_balance","total_monthly_salary", "vacation_due_amount"])
		
		encasement_details={}
		for res in resignation_list:
			encasement_details["employee_no"] = res.employee
			encasement_details["reference"] = res.name
			encasement_details["total_salary"] = res.total_monthly_salary
			encasement_details["due_amount"] = res.vacation_due_amount
			encasement_details["vacation_days"] = res.vacation_balance
			encasement_details["vacation_encasement_type"] = "Resignation"
			vacation_encasement_list.append(encasement_details)
			encasement_details = {}

		retriement_list = frappe.db.get_all("Retirement Request ST", filters={"creation_date": ["Between", [self.from_date, self.to_date]], "docstatus":1},
									  fields=["name", "employee_no","due_vacation_balance", "total_monthly_salary", "vacation_due_amount"])

		for ret in retriement_list:
			encasement_details["employee_no"] = ret.employee_no
			encasement_details["reference"] = ret.name
			encasement_details["total_salary"] = ret.total_monthly_salary
			encasement_details["due_amount"] = ret.vacation_due_amount
			encasement_details["vacation_days"] = ret	.due_vacation_balance
			encasement_details["vacation_encasement_type"] = "Retirement"
			vacation_encasement_list.append(encasement_details)
			encasement_details = {}

		vacation_sheet_list = frappe.db.get_all("Vacation Encasement Sheet", filters={"docstatus":0, "name":["!=", self.name]}, fields=["name"])

		for sheet in vacation_sheet_list:
			vacation_sheet = frappe.get_doc("Vacation Encasement Sheet", sheet.name)
			for emp in vacation_sheet.employee_details:
				for a in vacation_encasement_list:	
					if emp.reference == a.get('reference'):
						vacation_encasement_list.remove(a)
				else:
					continue

		return vacation_encasement_list