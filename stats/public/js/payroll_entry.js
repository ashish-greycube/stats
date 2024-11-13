frappe.ui.form.on("Payroll Entry", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.employees.length == 0) {
            frm.set_df_property('custom_generate_deductions', 'hidden', 1)
        }
        else {
            frm.set_df_property('custom_generate_deductions', 'hidden', 0)
        }
    },
    custom_generate_deductions: function (frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }
        else {
            // lwp deduction
            frappe.call({
                method: "stats.api.calculate_lwp_dedution",
                args: {
                    payroll_entry: frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message, '--r.message')
                    let lwp_deduction_list = r.message
                    if (lwp_deduction_list.length > 0) {
                        lwp_deduction_list.forEach((ele) => {
                            frm.doc.employees.forEach((row) => {
                                if (ele.employee == row.employee)
                                    frappe.model.set_value(row.doctype, row.name, "custom_lwp_deduction", ele.lwp_deduction)
                            })
                        })
                        // frm.refresh_field('employees')
                        // frm.save()
                    }
                }
            }),

            // absent Deduction
            frappe.call({
                method: "stats.api.calculate_absent_dedution",
                args: {
                    payroll_entry: frm.doc.name
                },
                callback: function (r) {
                    console.log(r.message, '--r.message')
                    let absent_deduction_list = r.message
                    if (absent_deduction_list.length > 0) {
                        absent_deduction_list.forEach((ele) => {
                            frm.doc.employees.forEach((row) => {
                                if (ele.employee == row.employee)
                                    frappe.model.set_value(row.doctype, row.name, "custom_absent_deduction", ele.absent_deduction)
                            })
                        })
                        // frm.refresh_field('employees')
                        // frm.save()
                    }
                }
            })

            setTimeout(() => {
                frm.refresh_field('employees')
                frm.save()
            }, 1000);

            
        }
    }
})