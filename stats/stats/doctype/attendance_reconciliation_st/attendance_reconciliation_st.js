// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Reconciliation ST", {
    onload(frm) {
        let month = frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()
        // let name = frappe.utils.get_datetime(frappe.datetime.get_today()).strftime("%B %Y")
        console.log(month,"-=-")
    },

    fetch(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("attendance_reconciliation_details", "");
        frm.call("fetch_attendance_details").then((r) => {
            let reconciliation_data = r.message
            if (reconciliation_data.length > 0) {
                reconciliation_data.forEach((ele) => {
                    var d = frm.add_child("attendance_reconciliation_details");
                    frappe.model.set_value(d.doctype, d.name, "date", ele.date)
                    frappe.model.set_value(d.doctype, d.name, "type", ele.type)
                    frappe.model.set_value(d.doctype, d.name, "delay_in", ele.delay_in)
                    frappe.model.set_value(d.doctype, d.name, "early_out", ele.early_out)
                })
                frm.refresh_field('attendance_reconciliation_details')
                frm.save()
            }
        })
    }
});
