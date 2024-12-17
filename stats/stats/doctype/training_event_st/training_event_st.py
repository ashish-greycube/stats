# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form, getdate, date_diff
from frappe.model.document import Document
from erpnext.manufacturing.doctype.workstation.workstation import get_default_holiday_list


class TrainingEventST(Document):
	def validate(self):
		self.validate_start_date_and_end_date()
		self.calculate_no_of_days()

	def validate_start_date_and_end_date(self):
		if self.training_start_date and self.training_end_date:
			if self.training_end_date < self.training_start_date:
				frappe.throw(_("End date can not be less than Start date"))

	def calculate_no_of_days(self):

		if self.training_start_date and self.training_end_date:
			no_of_day = date_diff(self.training_end_date, self.training_start_date) + 1

			if self.ignore_holidays_in_no_of_days == 1:
				fiscal_year_doc = frappe.get_doc("Fiscal Year",getdate(self.training_start_date).year)
				exist_holiday_list = frappe.db.get_all("Holiday List",
											filters={"to_date":fiscal_year_doc.year_end_date,"from_date":fiscal_year_doc.year_start_date},
											fields=["name"],limit=1)
				if len(exist_holiday_list)<1:
					frappe.throw(_("Holiday list for year <b>{0}</b> does not exists. Hence we cannot get holiday to ignore").format(getdate(self.training_start_date).year))

				holiday_count = 0
				if exist_holiday_list:
					holidays = frappe.db.get_all("Holiday",
										parent_doctype="Holiday List",
										filters={"parent":exist_holiday_list[0].name,"holiday_date":["between",[self.training_start_date,self.training_end_date]]},
										fields=["name"])
					if len(holidays)>0:
						holiday_count = len(holidays)
				
				self.no_of_days = no_of_day - holiday_count
			else :
				self.no_of_days = no_of_day
		

	def on_submit(self):
		if self.training_status == "Closed":
			if len(self.training_event_employee_details)>0:
				for row in self.training_event_employee_details:
					frappe.db.set_value("Training Request ST",row.training_request_reference,"status","Finished")
					frappe.msgprint(_("Status of {0} is changed to {1}").format(get_link_to_form("Training Request ST", row.training_request_reference),"Finished"),alert=1)
					create_training_evaluation(self.name,row.employee_no)
					frappe.db.set_value("Training Event ST",self.name,"training_status","Finished")
		
	@frappe.whitelist()
	def fetch_training_request(self):
		approved_training_request_list = frappe.db.get_all("Training Request ST",
													 filters = {"training_event":self.name,"docstatus":1,"status":"Accepted"},
													 fields=["name"])
		return approved_training_request_list

def create_training_evaluation(training_event,employee):
		training_evaluation_doc = frappe.new_doc("Training Evaluation ST")
		training_evaluation_doc.employee_no = employee
		training_evaluation_doc.training_event = training_event
		training_evaluation_doc.run_method("set_missing_values")
		training_evaluation_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Training Evaluation is created {0}").format(get_link_to_form("Training Evaluation ST",training_evaluation_doc.name)),alert=True)
		return training_evaluation_doc.name