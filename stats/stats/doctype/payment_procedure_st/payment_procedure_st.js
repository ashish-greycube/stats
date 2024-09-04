// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Procedure ST", {
    setup(frm) {
        frm.set_query("budget_account", function (doc) {
            return {
                query: "stats.stats.doctype.department_budget_st.department_budget_st.get_budget_account",
            };
        })
    },
	party_type(frm){
        if (frm.doc.party_type == "Employee"){
            frm.set_value("party_name_employee","Multiple Payment")
        }
    },
});
