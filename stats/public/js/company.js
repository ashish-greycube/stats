frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_business_trip_budget_expense_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": ["in",["Expense Account", "Indirect Expense"]]
                }
            };
        })
        frm.set_query("custom_business_trip_budget_chargeable_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Chargeable"
                }
            };
        })
    }
})