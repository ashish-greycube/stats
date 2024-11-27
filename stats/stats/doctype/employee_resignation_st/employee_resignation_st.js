// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation ST", {
    refresh(frm) {
        if(frm.doc.docstatus==1){
            frm.add_custom_button(__('End of Service'), () => create_end_of_service(frm));
            frm.add_custom_button(__('Evacuation of Party'), () => create_evacuation_of_party(frm));
            frm.add_custom_button(__('Exit Interview'), () => create_exit_interview(frm));
        }

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

let create_end_of_service = function (frm) {
    if (frm.is_dirty() == true) {
        frappe.throw({
            message: __("Please save the form to proceed..."),
            indicator: "red",
        });
    }

    frm.call("create_end_of_service").then((r) => {
        if (r.message) {
            console.log(r.message, "r.message")
            frappe.open_in_new_tab = true;
            frappe.set_route("Form", "End of Service Calculation ST", r.message);
            // window.open(`app/end-of-service-calculation-st/` + r.message);
        }
    })
}

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
            // window.open(`app/end-of-service-calculation-st/` + r.message);
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
            // window.open(`app/end-of-service-calculation-st/` + r.message);
        }
    })
}
