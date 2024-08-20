// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Man Power Plan Change Request ST", {
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
    job_no(frm){
        if(frm.doc.job_no){
            frappe.call({
				method: "stats.stats.doctype.opening_job_st.opening_job_st.get_job_deatils",
				args: {
					job_title: frm.doc.job_no
				}
			}).then(r => {
                if (r.message){
                    frm.set_value({
                        salary: r.message.salary,
                        grade: r.message.grade,
                        designation: r.message.designation,
                        pre_main_department: r.message.main_job_department,
                        pre_sub_department: r.message.sub_job_department,  
                    })
                }
            })
        }
    }
});
