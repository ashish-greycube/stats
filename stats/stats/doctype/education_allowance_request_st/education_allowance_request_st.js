// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Education Allowance Request ST", {

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['name','department','custom_sub_department','employee_name','grade','custom_section'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                    frm.set_value('employee_name', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                    frm.set_value('section', values.custom_section)
                    frm.set_value('grade', values.grade)
                })
        }
    },

	employee_no(frm) {
        frm.set_value("education_allowance_request_details","")
        frm.call("get_employee_dependants").then(
            r => {
                let family_details = r.message
                if (family_details) {
                    family_details.forEach((e) => {
                        var d = frm.add_child("education_allowance_request_details");
                        frappe.model.set_value(d.doctype, d.name, "child_name", e.name)
                        frappe.model.set_value(d.doctype, d.name, "relation", e.relation)
                        frappe.model.set_value(d.doctype, d.name, "date_of_birth", e.date_of_birth)
                    });
                    refresh_field("education_allowance_request_details");
                }
            }
        )
	},
});
