// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accumulative Budget ST", {
	department_budget_requests(frm){
        frm.set_value("account_details", "");
        frm.call({
            doc: frm.doc,
            method: "get_department_budget_requests",
            freeze: true,
            callback: (r) => {
                if (r.message) {
                    // console.log(r.message,'--------msg')
                    r.message.forEach((e) => {
                        // console.log(e)
                        // console.log(e, '--------e')
                        var d = frm.add_child("account_details");
                        frappe.model.set_value(d.doctype, d.name, "budget_expense_account", e.budget_expense_account)
                        frappe.model.set_value(d.doctype, d.name, "total_requested_amount", e.total_requested_amount)
                    });
                    refresh_field("account_details");
                    frm.save()
                }
            },
        });
    },
    allocate_department_wise_budget(frm){
        frm.set_value("department_wise_budget_allocation_details", "")
        frm.call({
            doc: frm.doc,
            method: "get_department_wise_budegt_allocation",
            freeze: true,
            callback: (r) => {
                if (r.message) {
                    console.log(r.message,'--------message')
                    r.message.forEach((e) => {
                        console.log(e)
                        console.log(e, '--------e')
                        var d = frm.add_child("department_wise_budget_allocation_details");
                        frappe.model.set_value(d.doctype, d.name, "main_department", e.main_department)
                        frappe.model.set_value(d.doctype, d.name, "budget_expense_account", e.budget_expense_account)
                        frappe.model.set_value(d.doctype, d.name, "requested_amount", e.requested_amount)
                        frappe.model.set_value(d.doctype, d.name, "approved_amount", e.approved_amount)
                    });
                    refresh_field("department_wise_budget_allocation_details");
                    frm.save()
                }
            },
        });
    }
});

frappe.ui.form.on("Accumulative Budget Details ST", {
    approved_amount(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        let difference = row.requested_amount - row.approved_amount
        frappe.model.set_value(cdt, cdn, "difference", difference)
    }
})
