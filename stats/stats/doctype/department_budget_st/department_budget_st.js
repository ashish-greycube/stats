// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Budget ST", {
    onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
            .then(r => {
                let values = r.message;
                frm.set_value('requested_by', values.name)
            })
        }  
    },
    setup(frm) {
        frm.set_query("budget_expense_account","account_table", function (doc,cdt,cdn) {
            return {
                query: "stats.stats.doctype.department_budget_st.department_budget_st.get_budget_account",
                // filters: {
                //     "company": frm.doc.name,
                //     "is_group": 0,
                //     "account_type": "Expense Account"
                // }
            };
        })
    }
});
