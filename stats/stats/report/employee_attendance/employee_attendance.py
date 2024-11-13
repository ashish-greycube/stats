# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _


def execute(filters=None):

	columns, data = [], []

	columns = get_columns(filters)
	data=get_attendance_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data


def get_columns(filters):
	return [
		{
			"fieldname": "employee",
			"label":_("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width":"300"
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
			"fieldname": "actual_delay",
			"label":_("Actual Delay"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "net_delay",
			"label":_("Net Delay"),
			"fieldtype": "Int",
			"width":"200"
		},
		{
			"fieldname": "actual_early",
			"label":_("Early"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "net_early",
			"label":_("Net Early"),
			"fieldtype": "Int",
			"width":"200"
		},
		{
			"fieldname": "extra_hours",
			"label":_("Extra Hours"),
			"fieldtype": "Int",
			"width":"200"
		},
		{
			"fieldname": "net_extra_hours",
			"label":_("Net Extra Hours"),
			"fieldtype": "Int",
			"width":"200"
		},
		{
			"fieldname": "no_of_hours",
			"label":_("No of Hours"),
			"fieldtype": "Float",
			"width":"200"
		},
		{
			"fieldname": "net_no_of_hours",
			"label":_("Net No of Hours"),
			"fieldtype": "Float",
			"width":"200"
		},
		{
			"fieldname": "date",
			"label":_("Date"),
			"fieldtype": "Date",
			"width":"300"
		}
	]

def get_attendance_data(filters):
	conditions = get_conditions(filters)

	attendance_data = frappe.db.sql("""
				SELECT
					employee,
					employee_name,
					attendance_date as date, 
					late_entry as actual_delay,
					early_exit as actual_early,
					custom_extra_minutes as extra_hours,
					in_time,
					out_time,
					working_hours as no_of_hours,
					custom_net_working_minutes as net_no_of_hours,
					custom_net_delay as net_delay,
					custom_net_early as net_early,
					custom_net_extra_hours as net_extra_hours,
					status
				from
					`tabAttendance`
				where {0}
		 """.format(conditions),filters,as_dict=1,debug=1)
	return attendance_data

def get_conditions(filters):
	conditions =""
	
	if filters.from_date:
		conditions += "attendance_date >= %(from_date)s "
	
	if filters.to_date:
		conditions += "and attendance_date <= %(to_date)s"

	if filters.employee:
		conditions += "and employee = %(employee)s "

	return conditions
