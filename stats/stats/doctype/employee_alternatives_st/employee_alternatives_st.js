// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Alternatives ST", {
    onload(frm) {
        // if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('request_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                })
        // }
    },

    fetch_employees(frm){
        frm.call("fetch_employees_based_on_filters").then(r => {
            console.log("r", r)
        })
    },
});
