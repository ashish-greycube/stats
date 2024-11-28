frappe.ui.form.on("Purchase Order", {
    onload(frm) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
            .then(r => {
                let values = r.message;
                frm.set_value('custom_created_by', values.employee_name)
                frm.set_value('custom_main_department', values.department)
                frm.set_value('custom_sub_department', values.custom_sub_department)
            })
    },
})