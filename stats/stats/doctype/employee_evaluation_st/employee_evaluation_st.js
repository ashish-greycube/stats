// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Evaluation ST", {

    setup: function (frm) {
        frm.trigger("hide_grid_add_row");
    },

    hide_grid_add_row: function (frm) {
        setTimeout(() => {
            frm.fields_dict.employee_personal_goals.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_job_goals.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_management_skills.grid.wrapper
                .find(".grid-add-row")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_personal_goals.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_job_goals.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);

        setTimeout(() => {
            frm.fields_dict.employee_management_skills.grid.wrapper
                .find(".grid-remove-rows")
                .remove();
        }, 100);
    },

    fetch_goals(frm) {
        if (frm.is_dirty() == true) {
            frappe.throw({
                message: __("Please save the form to proceed..."),
                indicator: "red",
            });
        }

        frm.set_value("employee_personal_goals", "");
        frm.set_value("employee_job_goals", "")
        frm.set_value("employee_management_skills", "")

        frm.call("fetch_employee_different_goals").then((r) => {
            console.log(r, "r")
            let employee_personal_goals = r.message[0]
            let employee_job_goals = r.message[1]
            let employee_management_skills = r.message[2]

            if (employee_personal_goals.length > 0) {
                employee_personal_goals.forEach((ele) => {
                    var d = frm.add_child("employee_personal_goals");
                    frappe.model.set_value(d.doctype, d.name, "goals", ele.goals)
                    frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                    frappe.model.set_value(d.doctype, d.name, "target_degree", ele.target_degree)
                })
                frm.refresh_field('employee_personal_goals')
            }

            if (employee_job_goals.length > 0) {
                employee_job_goals.forEach((ele) => {
                    var d = frm.add_child("employee_job_goals");
                    frappe.model.set_value(d.doctype, d.name, "goals", ele.goals)
                    frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                    frappe.model.set_value(d.doctype, d.name, "uom", ele.uom)
                    frappe.model.set_value(d.doctype, d.name, "target_degree", ele.target_degree)
                })
                frm.refresh_field('employee_job_goals')
            }

            if (employee_management_skills.length > 0) {
                employee_management_skills.forEach((ele) => {
                    var d = frm.add_child("employee_management_skills");
                    frappe.model.set_value(d.doctype, d.name, "skill", ele.skill)
                    frappe.model.set_value(d.doctype, d.name, "skill_description", ele.skill_description)
                    frappe.model.set_value(d.doctype, d.name, "weight", ele.weight)
                    frappe.model.set_value(d.doctype, d.name, "target_degree", ele.target_degree)
                })
                frm.refresh_field('employee_management_skills')
            }

            frm.save()
        })
    },

});

frappe.ui.form.on("Employee Personal Goals Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

frappe.ui.form.on("Employee Job Goals Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

frappe.ui.form.on("Employee Management Skills Details ST", {
    actual_degree(frm, cdt, cdn) {
        calculate_degree_based_on_weight(frm, cdt, cdn)
    }
});

let calculate_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.actual_degree && row.weight) {
        let actual_degree_based_on_weight = (row.actual_degree * row.weight) / 100
        frappe.model.set_value(cdt, cdn, "actual_degree_based_on_weight", actual_degree_based_on_weight)
    }
}
