// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Man Power Planning ST", {
	setup(frm) {
        frm.set_query("main_department", function (doc) {
			return {
				query: "stats.api.get_main_department",
			};
		});
		// frm.set_query("sub_department","job_details", function (doc,cdt,cdn){
        //     if (frm.doc.main_department) {
        //         return {
        //             filters: {
        //                 parent_department: frm.doc.main_department,
        //                 is_group: 0
        //             }
        //         };       
        //     }
		// })
        frm.set_query("job_family","job_details", function (doc,cdt,cdn){
                return {
                    query: "stats.api.get_main_job_family",
                }
		});
        frm.set_query("sub_job_family","job_details", function (doc,cdt,cdn){
                let row = locals[cdt][cdn]
                return {
                    filters: {
                        parent_job_family_st: row.job_family,
                        is_group: 0
                    }
                };
		})
    },

    supplier(frm) {
        if(frm.doc.supplier) {
            frappe.call({
				method: "stats.api.get_supplier_contact",
				args: {
					supplier: frm.doc.supplier
				}
			}).then(r => {
                if (r.message){
                    frm.set_value('contact_name', r.message)
                }
            })
        }
    }
});
