// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Trip Request ST", {
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

    business_trip_start_date(frm) {
        set_no_of_days(frm)
    },

    business_trip_end_date(frm){
        set_no_of_days(frm)
    }

});

let set_no_of_days = function (frm) {
    let start_date = frm.doc.business_trip_start_date
    let end_date = frm.doc.business_trip_end_date
    if (start_date && end_date) {
        let no_of_day = frappe.datetime.get_day_diff(end_date, start_date)
        frm.set_value("no_of_days", no_of_day)
    }

}