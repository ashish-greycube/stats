// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Petty Cash Closing ST", {
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

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
                .then(r => {
                    let values = r.message;
                    frm.set_value('created_by', values.employee_name)
                    frm.set_value('main_department', values.department)
                    frm.set_value('sub_department', values.custom_sub_department)
                })
        }
    },

    refresh(frm) {
        if (frm.doc.total_unpaid_amount > 0 && frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Petty Cash Re-Payment'), () => create_petty_cash_repayment_from_pc_closing(frm));
        }
    },
});

frappe.ui.form.on("PC Closing Account Details ST", {
    paid_amount(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        let unpaid_amount = row.amount - row.paid_amount
        frappe.model.set_value(cdt, cdn, "unpaid_amount", unpaid_amount)
    }
})

let create_petty_cash_repayment_from_pc_closing = function (frm) {
    frm.call("create_petty_cash_repayment").then(r => {
        let pc_repayment = r.message
        frappe.open_in_new_tab = true;
        frappe.set_route("Form", "Petty Cash Re-Payment ST", pc_repayment);
    })
}