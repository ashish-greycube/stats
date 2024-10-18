// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Request ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('employee', values.name)
            })
        }  
    },
    setup(frm) {
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("sub_department", function (doc) {
            if (frm.doc.main_department) {
                return {
                    filters: {
                        parent_department: frm.doc.main_department,
                        is_group: 0
                    }
                };
            }
        })
    },
    fetch_employee(frm){
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_overtime_request", "");
        frm.call({
            doc: frm.doc,
            method: "get_employee",
            freeze: true,
            callback: (r) => {
                let employee_list = r.message
                console.log(employee_list, '--list')
                if (employee_list) {
                    employee_list.forEach((e) => {
                        var d = frm.add_child("employee_overtime_request");
                        frappe.model.set_value(d.doctype, d.name, "employee_no", e.employee_no)
                    });
                    refresh_field("employee_overtime_request");
                    frm.save()
                }
            },
        });
    }
});
