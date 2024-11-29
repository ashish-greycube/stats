// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Retirement Request ST", {
	setup(frm) {
        frm.set_query("employee_no", function (doc) {
            return {
                query: "stats.stats.doctype.retirement_request_st.retirement_request_st.get_civil_employee",
            };
        })
	},
    refresh(frm) {
        if(frm.doc.docstatus==0){
            frm.add_custom_button(__('Evacuation of Party'), () => create_evacuation_of_party(frm));
            frm.add_custom_button(__('Exit Interview'), () => create_exit_interview(frm));
        }
    },
});

let create_evacuation_of_party = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }

    frm.call("create_evacuation_of_party").then((r) => {
        if (r.message) {
            console.log(r.message, "r.message")
            frappe.open_in_new_tab = true;
            frappe.set_route("Form", "Evacuation of Party ST", r.message);
        }
    })
}

let create_exit_interview = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }
    
    frm.call("create_exit_interview").then((r)=>{
        if (r.message) {
            console.log(r.message, "r.message")
            frappe.open_in_new_tab = true;
            frappe.set_route("Form", "Exit Interview ST", r.message);
        }
    })
}