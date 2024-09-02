// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Request ST", {
    party_type(frm){
        if (frm.doc.party_type == "Employee"){
            frm.set_value("party_name_employee","Multiple Payment")
        }
    },
});
