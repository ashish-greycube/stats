import frappe
from frappe import _
from frappe.utils import (add_to_date, get_datetime, getdate, nowdate, get_first_day)
from stats.stats.report.employee_attendance.employee_attendance import calculate_incomplete_total_monthly_minutes

########### LWP Deduction ###########

def get_non_working_days(employee, payroll_start_date, payroll_end_date) -> float:
	filters = {
		"docstatus": 1,
		"status": "On Leave",
		"employee": employee,
		"attendance_date": ("between", [get_datetime(payroll_start_date), get_datetime(payroll_end_date)]),
	}

	# if status == "On Leave":
	lwp_leave_types = frappe.get_all("Leave Type", filters={"is_lwp": 1}, pluck="name")
	filters["leave_type"] = ("IN", lwp_leave_types)

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(*) as total_lwp"])
	return record[0].total_lwp if len(record) else 0

@frappe.whitelist()
def calculate_lwp_dedution(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)

	print(previous_month_last_date, previous_month_start_date,'----------previous_month_last_date-----------')

	emp_dedution_list = []
	for emp in payroll_entry.employees:
		total_lwp = get_non_working_days(emp.employee,previous_month_start_date, previous_month_last_date)
		print(total_lwp, '--total_lwp')
	
		emp_dedution_details = {}
		
		if total_lwp > 0:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee}, 
								  order_by = "from_date desc", limit=1)
			print(salary_assignment[0].name, '--salary_assignment')
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
				
				total_lwp_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						per_day_salary = (ear.amount)/30
						total_lwp_deduction = total_lwp_deduction + (per_day_salary * total_lwp)

				emp_dedution_details['employee'] = emp.employee
				emp_dedution_details['lwp_deduction'] = total_lwp_deduction
				print(total_lwp_deduction, '---total_lwp_deduction')

				emp_dedution_list.append(emp_dedution_details)

		else:	
			emp_dedution_details['employee'] = emp.employee
			emp_dedution_details['lwp_deduction'] = 0

			emp_dedution_list.append(emp_dedution_details)
				
	return emp_dedution_list

########### Absent Deduction ###########

def get_absent_days(employee, payroll_start_date, payroll_end_date) -> float:
	filters = {
		"docstatus": 1,
		"status": "Absent",
		"employee": employee,
		"attendance_date": ("between", [get_datetime(payroll_start_date), get_datetime(payroll_end_date)]),
	}

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(*) as total_absent"])
	return record[0].total_absent if len(record) else 0


@frappe.whitelist()
def calculate_absent_dedution(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)

	print(previous_month_last_date, previous_month_start_date,'----------previous_month_last_date-----------')

	emp_dedution_list = []
	for emp in payroll_entry.employees:
		total_absent = get_absent_days(emp.employee, previous_month_start_date, previous_month_last_date)
		print(total_absent, '--total_absent')
	
		emp_dedution_details = {}
		
		if total_absent > 0:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee}, 
								  order_by = "from_date desc", limit=1)
			print(salary_assignment[0].name, '--salary_assignment')
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
				
				total_absent_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						per_day_salary = (ear.amount)/30
						total_absent_deduction = total_absent_deduction + (per_day_salary * total_absent)

				emp_dedution_details['employee'] = emp.employee
				emp_dedution_details['absent_deduction'] = total_absent_deduction
				print(total_absent_deduction, '---total_absent_deduction')

				emp_dedution_list.append(emp_dedution_details)

		else:	
			emp_dedution_details['employee'] = emp.employee
			emp_dedution_details['absent_deduction'] = 0

			emp_dedution_list.append(emp_dedution_details)
				
	return emp_dedution_list

########### Incomplete Monthly Mins Deduction ###########

@frappe.whitelist()
def calculate_incomplete_monthly_mins_deduction(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_start_date = add_to_date(payroll_entry.start_date,months=-1)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)
	print(payroll_entry.name, "000=======payroll_entry======")

	emp_monthly_incomplete_mins_list = []
	for emp in payroll_entry.employees:

		total_incomplete_monthly_mins = calculate_incomplete_total_monthly_minutes(emp.employee, previous_month_start_date, previous_month_last_date)
		contract_type = frappe.db.get_value("Employee", emp.employee, "custom_contract_type")
		total_mins_per_month = frappe.db.get_value("Contract Type ST", contract_type, "total_mins_per_month")
		total_hours_per_day = frappe.db.get_value("Contract Type ST", contract_type, "total_hours_per_day")

		emp_incomplete_mins_details = {}

		print(total_incomplete_monthly_mins, "---total_incomplete_monthly_mins")
		print(total_mins_per_month, "======total_mins_per_month")
		if total_incomplete_monthly_mins < total_mins_per_month:

			salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", payroll_entry.start_date], "employee":emp.employee}, 
								  order_by = "from_date desc", limit=1)
			
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
				total_incomplete_mins_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						per_mins_salary = (ear.amount)/(30 * total_hours_per_day * 60)
						total_incomplete_mins_deduction = total_incomplete_mins_deduction + (per_mins_salary * total_incomplete_monthly_mins)

						emp_incomplete_mins_details['employee'] = emp.employee
						emp_incomplete_mins_details['incomplete_mins_deduction'] = total_incomplete_mins_deduction
						print(total_incomplete_mins_deduction, '---total_incomplete_mins_deduction')

						emp_monthly_incomplete_mins_list.append(emp_incomplete_mins_details)

		else:
			emp_incomplete_mins_details['employee'] = emp.employee
			emp_incomplete_mins_details['incomplete_mins_deduction'] = 0

			emp_monthly_incomplete_mins_list.append(emp_incomplete_mins_details)
		
	return emp_monthly_incomplete_mins_list


########### Deduction Additional Salary ###########

def create_additonal_salary_for_deduction(self, method):

	lwp_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'lwpabsent_deduction_component')
	absent_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'absent_deduction_component')
	incomplete_monthly_mins_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'incomplete_monthly_mins_deduction_component')

	for emp in self.employees:
		if emp.custom_lwp_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  lwp_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_lwp_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for LWP Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()

		if emp.custom_absent_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  absent_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_absent_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Absent Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()

		if emp.custom_incomplete_monthly_mins_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  incomplete_monthly_mins_deduction_component
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.amount = emp.custom_incomplete_monthly_mins_deduction
			additional_salary.save(ignore_permissions=True)
			additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Incomplete Monthly Mins Deduction'.format(nowdate()))
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()
			

########### Employee Resignation Additional Salary ###########

def create_resignation_addition_salary_for_employee(self, method):
	relieving_date_changed = self.has_value_changed("relieving_date")

	print(relieving_date_changed, '----------relieving_date_changed')
	if relieving_date_changed and self.relieving_date != None:
		salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", nowdate()], "employee":self.name}, 
								  order_by = "from_date desc", limit=1)
		print(salary_assignment[0].name, '--salary_assignment')
		if len(salary_assignment) > 0:
			ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
		
			total_deduction = 0
			for ear in ss.earnings:
				deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
				if deduction_component == 1:
					per_day_salary = (ear.amount)/30
					days_after_resignation = 30 - getdate(self.relieving_date).day
					total_deduction = (total_deduction) + (per_day_salary * days_after_resignation)
				

			if total_deduction > 0:
				resignation_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'resignation_deduction_component')
				print(resignation_deduction_component, '--resignation_deduction_component')
				if not resignation_deduction_component:
					frappe.throw(_("Please Set Resignation Deduction in Stats Settings Doctype"))
				else:
					next_month_date = add_to_date(self.relieving_date, months=1)

					additional_salary = frappe.new_doc("Additional Salary")
					additional_salary.employee = self.name
					# additional_salary.payroll_date =  get_first_day(next_month_date)
					additional_salary.payroll_date = get_first_day(self.relieving_date)
					print(self.relieving_date, additional_salary.payroll_date, '--------')
					additional_salary.salary_component =  resignation_deduction_component
					additional_salary.overwrite_salary_structure_amount = 0
					additional_salary.amount = total_deduction
					additional_salary.save(ignore_permissions=True)
					additional_salary.add_comment('Comment', 'This Additonal Salary is created on {0} for Resignation Deduction'.format(nowdate()))
					frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, self.name), alert=1)
					additional_salary.submit()


def get_latest_salary_structure_assignment(employee, from_date):
	salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure", "base"], filters={"from_date": ["<=", from_date], "employee":employee}, 
								  order_by = "from_date desc", limit=1)
	if len(salary_assignment) > 0:
		return salary_assignment[0].name
	else:
		frappe.throw(_("For {0} date No Salary Structure Assignment Found for {1} Employee").format(from_date, employee))
