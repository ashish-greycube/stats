// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Final Statistic Processing ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
            })
        }  
    },
});
