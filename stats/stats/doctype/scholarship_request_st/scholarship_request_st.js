// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Scholarship Request ST", {
    setup(frm) {
        frm.set_query("scholarship_no",function (doc){
            return {
                query: "stats.stats.doctype.scholarship_request_st.scholarship_request_st.get_open_scholarships"
            };
        });
        frm.set_query("specialisation_type", function(doc){
            if (frm.doc.scholarship_no){
                return {
                    query:"stats.stats.doctype.scholarship_request_st.scholarship_request_st.get_specialisation_type_from_scholarship_no",
                    filters : {
                        scholarship_no : frm.doc.scholarship_no
                    }
                }
            }
        })
    },

    onload(frm) {
        if (frm.is_new()) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    let values = r.message;
                    frm.set_value('employee_no', values.name)
                })
        }
    },

    specialisation_type(frm) {
        if (frm.doc.specialisation_type) {
            frm.call("fetch_scholarship_details_based_on_specialisation_type").then((r) => {
                let scholarship_detail_list = r.message
                if (scholarship_detail_list.length > 0) {
                    frm.set_value("qualification", scholarship_detail_list[0].qualification)
                    frm.set_value("scholarship_start_date", scholarship_detail_list[0].scholarship_start_date)
                    frm.set_value("scholarship_end_date", scholarship_detail_list[0].scholarship_end_date)
                    frm.set_value("english_required", scholarship_detail_list[0].english_required)
                }
            })
        }
    }
});
