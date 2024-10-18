// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Attendance"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.add_days(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.get_today()
		},
	]
};
