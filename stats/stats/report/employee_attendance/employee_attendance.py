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
			"fieldname": "delay",
			"label":_("Delay"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "early",
			"label":_("Early"),
			"fieldtype": "Int",
			"width":"100"
		},
		{
			"fieldname": "extra_hours",
			"label":_("Extra Hours"),
			"fieldtype": "Float",
			"width":"200"
		},
		{
			"fieldname": "no_of_hours",
			"label":_("No of Hours"),
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
					late_entry as delay,
					early_exit as early,
					custom_extra_hours as extra_hours,
					in_time,
					out_time,
					working_hours as no_of_hours
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
