frappe.ui.form.on("Employee", {
    refresh(frm) {
        console.log("in setup")
        frm.set_query("department", function (doc) {
            console.log("Working")
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("custom_sub_department", function (doc) {
            if (frm.doc.department) {
                return {
                    filters: {
                        parent_department: frm.doc.department,
                        is_group: 0
                    }
                };
            }
        })
    }
})