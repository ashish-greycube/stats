// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Trip Sheet ST", {
	setup(frm) {
        frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		frm.set_query("sub_department", function (doc){
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
    fetch_business_trip(frm){
        frm.set_value("employee_detail", "");
        frm.call({
            doc: frm.doc,
            method: "get_business_trip",
            freeze: true,
            callback: (r) => {
                if (r.message) {
                    // console.log(r.message)
                    r.message.forEach((e) => {
                        // console.log(e)
                        var d = frm.add_child("employee_detail");
                        frappe.model.set_value(d.doctype, d.name, "employee_task_completion_reference", e.name)
                    });
                    refresh_field("employee_detail");
                    frm.save()
                }
            },
        });
    }
});
