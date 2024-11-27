// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Retirement Request ST", {
	setup(frm) {
        frm.set_query("employee_no", function (doc) {
            return {
                query: "stats.stats.doctype.retirement_request_st.retirement_request_st.get_civil_employee",
            };
        })
	},
});
