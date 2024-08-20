// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Opening Job ST", {
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

    job_title(frm){
        if(frm.doc.job_title){
            frappe.call({
				method: "stats.stats.doctype.opening_job_st.opening_job_st.get_job_deatils",
				args: {
					job_title: frm.doc.job_title
				}
			}).then(r => {
                if (r.message){
                    frm.set_value({
                        designation: r.message.designation,
                        main_department: r.message.main_job_department,
                        sub_department: r.message.sub_job_department,
                        grade: r.message.grade,
                        section: r.message.section
                    })
                }
            })
        }
    }
});
