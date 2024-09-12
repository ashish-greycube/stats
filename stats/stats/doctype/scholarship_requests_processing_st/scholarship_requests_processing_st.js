// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Scholarship Requests Processing ST", {
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
        });
        frm.set_query("specialisation_type", function (doc) {
            if (frm.doc.scholarship_no) {
                return {
                    query: "stats.stats.doctype.scholarship_requests_processing_st.scholarship_requests_processing_st.get_specialisation_type_from_scholarship_no",
                    filters: {
                        scholarship_no: frm.doc.scholarship_no
                    }
                }
            }
        });
        frm.set_query("scholarship_no", function (doc) {
            return {
                query: "stats.stats.doctype.scholarship_requests_processing_st.scholarship_requests_processing_st.get_open_scholarships"
            };
        });
    },

    scholarship_no(frm) {
        if (frm.doc.scholarship_no){
            frappe.db.get_doc('Scholarship ST', null, { scholarship_no: frm.doc.scholarship_no })
            .then(doc => {
                frappe.db.get_value('Scholarship ST', doc.name, 'scholarship_type')
                .then(r => {
                    console.log(r.message.scholarship_type) // Open
                    frm.set_value("scholarship_type",r.message.scholarship_type)
                })
                        })
        }
    },

    fetch_scholarship_requests(frm) {
        frm.set_value("scholarship_request_details", "");
        frm.call({
            doc: frm.doc,
            method: "get_scholarship_requests",
            freeze: true,
            callback: (r) => {
                let scholarship_request_list = r.message
                if (scholarship_request_list) {
                    scholarship_request_list.forEach((e) => {
                        var d = frm.add_child("scholarship_request_details");
                        frappe.model.set_value(d.doctype, d.name, "scholarship_request_reference", e.name)
                    });
                    refresh_field("scholarship_request_details");
                    frm.save()
                }
            },
        });
    }
});
