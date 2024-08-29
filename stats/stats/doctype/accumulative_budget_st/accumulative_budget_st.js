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
                        frappe.model.set_value(d.doctype, d.name, "account_name", e.account_name)
                        frappe.model.set_value(d.doctype, d.name, "requested_amount", e.requested_amount)
                    });
                    refresh_field("account_details");
                    frm.save()
                }
            },
        });
    }
});

// frappe.ui.form.on("Accumulative Budget ST", {
//     approved_amount(frm){
//         let row = locals[cdt][cdn]
//     }
// })
