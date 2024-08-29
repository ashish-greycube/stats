frappe.ui.form.on("Company", {
    setup(frm) {
        frm.set_query("custom_default_business_trip_budget_account", function (doc) {
            return {
                filters: {
                    "company": frm.doc.name,
                    "is_group": 0,
                    "account_type": "Expense Account"
                }
            };
        })
        frm.set_query("custom_default_business_trip_chargeable_account", function (doc) {
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