// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation ST", {
	setup(frm) {
        frm.set_query("main_department", function (doc) {
            return {
                query: "stats.api.get_main_department",
            };
        });
        frm.set_query("sub_department", function (doc) {
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

    resignation_type(frm) {
        frappe.db.get_value('Resignation Type ST', frm.doc.resignation_type, 'is_it_separation')
            .then(r => {
                console.log(r.message.is_it_separation)
                if(r.message.is_it_separation == 1){
                    frm.set_df_property('separation_reason', 'hidden', 0);
                }
                else{
                    frm.set_df_property('separation_reason', 'hidden', 1);   
                }
            })
    }
});
