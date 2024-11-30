# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinalStatisticProcessingST(Document):
	def validate(self):
		self.calculate_total_cost_department_vise()

	def on_submit(self):
		self.set_approval_status_in_statistic_request()

	def calculate_total_cost_department_vise(self):
		total_request_cost = 0
		if len(self.sub_department_1) > 0:
			total_cost_1 = 0
			for dep1 in self.sub_department_1:
				total_cost_1 = total_cost_1 + (dep1.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_1
			self.total_cost_1 = total_cost_1

		if len(self.sub_department_2) > 0:
			total_cost_2 = 0
			for dep2 in self.sub_department_2:
				total_cost_2 = total_cost_2 + (dep2.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_2
			self.total_cost_2 = total_cost_2

		if len(self.sub_department_3) > 0:
			total_cost_3 = 0
			for dep3 in self.sub_department_3:
				total_cost_3 = total_cost_3 + (dep3.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_3
			self.total_cost_3 = total_cost_3

		if len(self.sub_department_4) > 0:
			total_cost_4 = 0
			for dep4 in self.sub_department_4:
				total_cost_4 = total_cost_4 + (dep4.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_4
			self.total_cost_4 = total_cost_4

		if len(self.sub_department_5) > 0:
			total_cost_5 = 0
			for dep5 in self.sub_department_5:
				total_cost_5 = total_cost_5 + (dep5.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_5
			self.total_cost_5 = total_cost_5
		
		if len(self.sub_department_6) > 0:
			total_cost_6 = 0
			for dep6 in self.sub_department_6:
				total_cost_6 = total_cost_6 + (dep6.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_6
			self.total_cost_6 = total_cost_6
		
		if len(self.sub_department_7) > 0:
			total_cost_7 = 0
			for dep7 in self.sub_department_7:
				total_cost_7 = total_cost_7 + (dep7.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_7
			self.total_cost_7 = total_cost_7
		
		if len(self.sub_department_8) > 0:
			total_cost_8 = 0
			for dep8 in self.sub_department_8:
				total_cost_8 = total_cost_8 + (dep8.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_8
			self.total_cost_8 = total_cost_8

		if len(self.sub_department_9) > 0:
			total_cost_9 = 0
			for dep9 in self.sub_department_9:
				total_cost_9 = total_cost_9 + (dep9.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_9
			self.total_cost_9 = total_cost_9
		
		if len(self.sub_department_10) > 0:
			total_cost_10 = 0
			for dep10 in self.sub_department_10:
				total_cost_10 = total_cost_10 + (dep10.final_cost or 0)
			
			total_request_cost = total_request_cost + total_cost_10
			self.total_cost_10 = total_cost_10

		self.total_request_cost = total_request_cost
	
		# calculate percentage
		if total_request_cost > 0:
			self.percentage_1 = ((self.total_cost_1  or 0)* 100) / total_request_cost
			self.percentage_2 = ((self.total_cost_2  or 0)* 100) / total_request_cost
			self.percentage_3 = ((self.total_cost_3  or 0)* 100) / total_request_cost
			self.percentage_4 = ((self.total_cost_4  or 0)* 100) / total_request_cost
			self.percentage_5 = ((self.total_cost_5  or 0)* 100) / total_request_cost
			self.percentage_6 = ((self.total_cost_6  or 0)* 100) / total_request_cost
			self.percentage_7 = ((self.total_cost_7  or 0)* 100) / total_request_cost
			self.percentage_8 = ((self.total_cost_8  or 0)* 100) / total_request_cost
			self.percentage_9 = ((self.total_cost_9  or 0)* 100) / total_request_cost
			self.percentage_10 = ((self.total_cost_10 or 0) * 100) / total_request_cost

	def set_approval_status_in_statistic_request(self):
		if len(self.sub_department_1) > 0:
			for dep1 in self.sub_department_1:
				if dep1.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep1.statistic_request_reference, "Final Approval")
				elif dep1.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep1.statistic_request_reference, "Rejected")
				else:
					continue

		if len(self.sub_department_2) > 0:
			for dep2 in self.sub_department_2:
				if dep2.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep2.statistic_request_reference, "Final Approval")
				elif dep2.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep2.statistic_request_reference, "Rejected")
				else:
					continue

		if len(self.sub_department_3) > 0:
			for dep3 in self.sub_department_3:
				if dep3.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep3.statistic_request_reference, "Final Approval")
				elif dep3.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep3.statistic_request_reference, "Rejected")
				else:
					continue
					
		if len(self.sub_department_4) > 0:
			for dep4 in self.sub_department_4:
				if dep4.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep4.statistic_request_reference, "Final Approval")
				elif dep4.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep4.statistic_request_reference, "Rejected")
				else:
					continue
		
		if len(self.sub_department_5) > 0:
			for dep5 in self.sub_department_5:
				if dep5.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep5.statistic_request_reference, "Final Approval")
				elif dep5.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep5.statistic_request_reference, "Rejected")
				else:
					continue
		
		if len(self.sub_department_6) > 0:
			for dep6 in self.sub_department_6:
				if dep6.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep6.statistic_request_reference, "Final Approval")
				elif dep6.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep6.statistic_request_reference, "Rejected")
				else:
					continue
		
		if len(self.sub_department_7) > 0:
			for dep7 in self.sub_department_7:
				if dep7.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep7.statistic_request_reference, "Final Approval")
				elif dep7.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep7.statistic_request_reference, "Rejected")
				else:
					continue
		
		if len(self.sub_department_8) > 0:
			for dep8 in self.sub_department_8:
				if dep8.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep8.statistic_request_reference, "Final Approval")
				elif dep8.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep8.statistic_request_reference, "Rejected")
				else:
					continue

		if len(self.sub_department_9) > 0:
			for dep9 in self.sub_department_9:
				if dep9.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep9.statistic_request_reference, "Final Approval")
				elif dep9.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep9.statistic_request_reference, "Rejected")
				else:
					continue

		if len(self.sub_department_10) > 0:
			for dep10 in self.sub_department_10:
				if dep10.action == "Approve":
					frappe.db.set_value("Statistic Request ST", dep10.statistic_request_reference, "Final Approval")
				elif dep10.action == "Reject":
					frappe.db.set_value("Statistic Request ST", dep10.statistic_request_reference, "Rejected")
				else:
					continue