# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _


def execute(filters=None):

	columns, data = [], []

	columns = get_columns(filters)
	data, report_summary=get_attendance_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data, None, None, report_summary


def get_columns(filters):
	return [
		{
			"fieldname": "attendance",
			"label":_("Attendance"),
			"fieldtype": "Link",
			"options": "Attendance",
			"width":"200"
		},
		{
			"fieldname": "employee",
			"label":_("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":"200"
		},
		{
			"fieldname": "in_time",
			"label":_("In"),
			"fieldtype": "Datetime",
			"width":"200"
		},
		{
			"fieldname": "out_time",
			"label":_("Out"),
			"fieldtype": "Datetime",
			"width":"200"
		},
		{
			"fieldname": "status",
			"label":_("Status"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "working_minutes_per_day",
			"label":_("Working Minutes Per Day"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "actual_working_minutes",
			"label":_("Actual Working Minutes"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "net_working_minutes",
			"label":_("Net Working Minutes"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "difference_in_working_minutes",
			"label":_("Difference in Working Minutes"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "reconciliation_method",
			"label":_("Reconciliation Method"),
			"fieldtype": "Data",
			"width":"200"
		},
		{
			"fieldname": "extra_minutes",
			"label":_("Extra Minutes"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "actual_delay",
			"label":_("Actual Delay"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "actual_early",
			"label":_("Actual Early"),
			"fieldtype": "Int",
			"width":"100"
		}
	]

def get_attendance_data(filters):
	conditions = get_conditions(filters)

	attendance_data = frappe.db.sql("""
				SELECT
					name as attendance,
					employee,
					employee_name,
					in_time,
					out_time,
					custom_attendance_type as status,
					custom_working_minutes_per_day as working_minutes_per_day,
					custom_actual_working_minutes as actual_working_minutes,
					custom_net_working_minutes as net_working_minutes,
					custom_difference_in_working_minutes as difference_in_working_minutes,
					custom_reconciliation_method as reconciliation_method,
					custom_actual_delay_minutes as actual_delay,
					custom_actual_early_minutes as actual_early,
					custom_extra_minutes as extra_minutes
				from
					`tabAttendance`
				where {0}
		 """.format(conditions),filters,as_dict=1,debug=1)
	
	expected_total_monthly_minutes= get_expected_total_monthly_minutes_and_total_minutes_per_day(filters.employee)
	present_total_monthly_mins = get_total_present_minutes_per_month(filters)
	company_holiday_total_monthly_mins = get_company_holiday_count(filters.employee, filters.from_date, filters.to_date)
	incomplete_total_monthly_minutes= calculate_incomplete_total_monthly_minutes(filters.employee, filters.from_date, filters.to_date)

	report_summary=[
		{'label':'Expected Monthly Mins.(No Week Off) <br> irrespective of month days','value':expected_total_monthly_minutes},
		{'type':'separator','value':'-'},
		{'label':'Present Mins Per Month(Present+Paid Leaves)','value':present_total_monthly_mins},
		{'type':'separator','value':'-'},
		{'label':'Company Holiday Mins (Paid)','value':company_holiday_total_monthly_mins},
		{'type':'separator','value':'='},
		{'label':'Incomplete Working Mins (to be cut in salary)','value':incomplete_total_monthly_minutes}		
	]
	return attendance_data,report_summary

def get_conditions(filters):
	conditions =""
	
	if filters.from_date:
		conditions += "attendance_date >= %(from_date)s "
	
	if filters.to_date:
		conditions += "and attendance_date <= %(to_date)s"

	if filters.employee:
		conditions += "and employee = %(employee)s "

	return conditions

@frappe.whitelist()
def get_company_holiday_count(employee, from_date, to_date):

	company_holiday_count = 0
	current_holiday_list = frappe.db.get_all("Holiday List",
										filters={"from_date":["<=",from_date],"to_date":[">=",to_date]},
										fields=["name"])
	if len(current_holiday_list)>0:
		company_holidays = frappe.db.get_all("Holiday",
										parent_doctype="Holiday List",
										filters={"parent":current_holiday_list[0].name,"weekly_off":0,"holiday_date":["between",[from_date,to_date]]},
										fields=["description"])
		if len(company_holidays)>0:
			company_holiday_count = company_holiday_count + len(company_holidays)

		employee_contract_name = frappe.db.get_value("Employee",employee,"custom_contract_type")
		if employee_contract_name:
			total_minutes_per_day = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_mins_per_day"])
			company_holiday_minutes = company_holiday_count * total_minutes_per_day
	return company_holiday_minutes

@frappe.whitelist()
def get_total_present_minutes_per_month(filters):
	
	conditions = get_conditions(filters)
	total_monthly_mins = frappe.db.sql("""
				SELECT
					sum(custom_net_working_minutes) as mins
				from
					`tabAttendance`
				where {0} 
					and custom_attendance_type in ('Present', 'On LWP', 'In Training', 'Business Trip', 'Scholarship', 'Present Due To Reconciliation')
		""".format(conditions),filters,as_dict=1,debug=1)
	if len(total_monthly_mins)>0:
		present_total_monthly_mins = total_monthly_mins[0].mins
	return present_total_monthly_mins

@frappe.whitelist()
def get_expected_total_monthly_minutes_and_total_minutes_per_day(employee):
	employee_contract_name = frappe.db.get_value("Employee",employee,"custom_contract_type")
	if employee_contract_name:
		expected_monthly_minutes = frappe.db.get_value("Contract Type ST",employee_contract_name,["total_mins_per_month"])
		return expected_monthly_minutes

@frappe.whitelist()	
def calculate_incomplete_total_monthly_minutes(employee, from_date, to_date):
	filters=frappe._dict({"employee":employee, "from_date":from_date, "to_date":to_date})
	present_total_minutes_per_month = get_total_present_minutes_per_month(filters)
	expected_monthly_minutes= get_expected_total_monthly_minutes_and_total_minutes_per_day(employee)
	company_holiday_total_monthly_mins = get_company_holiday_count(employee,from_date,to_date)

	actual_total_monthly_mins = present_total_minutes_per_month + company_holiday_total_monthly_mins

	incomplete_total_monthly_mins = expected_monthly_minutes - actual_total_monthly_mins
	return incomplete_total_monthly_mins