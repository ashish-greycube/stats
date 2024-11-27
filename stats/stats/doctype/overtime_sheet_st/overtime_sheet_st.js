// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Sheet ST", {
	onload(frm) {
        if (frm.is_new()){
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'employee_name')
            .then(r => {
                let values = r.message;
                frm.set_value('created_by', values.employee_name)
            })
        }  
    },

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

    fetch_transactions(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("overtime_sheet_employee_details", "");
        frm.call("fetch_employees_from_overtime_request").then((r) => {
            let employee_list = r.message
            console.log(employee_list,"--------------")
            if (employee_list.length > 0) {
                employee_list.forEach((ele) => {
                    var d = frm.add_child("overtime_sheet_employee_details");
                    frappe.model.set_value(d.doctype, d.name, "overtime_request_reference", ele.overtime_request_reference)
                    frappe.model.set_value(d.doctype, d.name, "request_date", ele.requested_date)
                    frappe.model.set_value(d.doctype, d.name, "employee_no", ele.employee_no)
                    frappe.model.set_value(d.doctype, d.name, "employee_name", ele.employee_name)
                    frappe.model.set_value(d.doctype, d.name, "required_extra_hours", ele.required_extra_hours)
                    frappe.model.set_value(d.doctype, d.name, "actual_extra_hours", ele.actual_extra_hours)
                    frappe.model.set_value(d.doctype, d.name, "amount", ele.amount)
                    frappe.model.set_value(d.doctype, d.name, "overtime_rate_per_hour", ele.overtime_rate_per_hour)
                })
                frm.refresh_field('overtime_sheet_employee_details')
                // frm.save()
            }
        })
    }
});

frappe.ui.form.on("Overtime Sheet Employee Details ST", {
    actual_extra_hours(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (row.actual_extra_hours){
            let total_amount = row.actual_extra_hours * row.overtime_rate_per_hour
            frappe.model.set_value(row.doctype, row.name,"amount", total_amount)
        }
    }
})
