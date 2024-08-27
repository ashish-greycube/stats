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

    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Ticket Request'), () => create_ticket_request_from_business_trip_request(frm), __("Create"));
        }
        // if (!frm.is_new()) {
        //     frm.add_custom_button(__('Create Employee Task Completion'), () => create_task_completion_from_business_trip_request(frm), __("Create"));
        // }
    },

    business_trip_start_date(frm) {
        set_no_of_days(frm)
    },

    business_trip_end_date(frm) {
        set_no_of_days(frm)
    },

});

let set_no_of_days = function (frm) {
    let start_date = frm.doc.business_trip_start_date
    let end_date = frm.doc.business_trip_end_date
    if (start_date && end_date) {
        let no_of_day = frappe.datetime.get_day_diff(end_date, start_date)
        frm.set_value("no_of_days", no_of_day)
    }
}

let create_ticket_request_from_business_trip_request = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }

    frappe.call({
        method: "stats.stats.doctype.business_trip_request_st.business_trip_request_st.create_ticket_request_from_business_trip_request",
        args: {
            source_name: frm.doc.name
        },
        callback: function (r) {
            if (r.message) {
                window.open(`/app/ticket-request-st/` +  r.message);
            }
        }
    })
}

// let create_task_completion_from_business_trip_request = function (frm) {

// }