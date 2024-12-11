// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Education Allowance Request ST", {

    setup: function (frm) {
        frm.trigger("hide_grid_add_row");
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.education_allowance_request_details.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);
    },

    onload_post_render(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['name','department','custom_sub_department','employee_name','grade','custom_section'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                    frm.set_value('employee_name', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                    frm.set_value('section', values.custom_section)
                    frm.set_value('grade', values.grade).then(()=>set_grade_allowance_limit_value(frm))
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
                        frappe.model.set_value(d.doctype, d.name, "age", e.age)
                        frappe.model.set_value(d.doctype, d.name, "approved_amount", e.approved_amount)
                    });
                    refresh_field("education_allowance_request_details");
                }
            }
        )
	},

    
    grade(frm) {
        // do not remove

    }
});

function set_grade_allowance_limit_value(frm) {
    let grade = frm.doc.grade
    if (grade){
        frappe.db.get_value("Employee Grade",grade,"custom_education_allowance_amount").then(
            r => {
                console.log(r.message,r.message.custom_education_allowance_amount)
                if (r.message.custom_education_allowance_amount){
                    frm.set_value("allowance_limit",r.message.custom_education_allowance_amount)
                }
            }
        )
    }  
}