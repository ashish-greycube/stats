frappe.ui.form.on("Designation", {

})

frappe.ui.form.on("Competencies Details ST", {
    weight(frm,cdt,cdn){
        set_degree_based_on_weight(frm,cdt,cdn)
    },

    degree_out_of_5(frm,cdt,cdn){
        set_degree_based_on_weight(frm,cdt,cdn)
    }
})

let set_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.weight && row.degree_out_of_5) {
        let degree_based_on_weight = (row.weight * row.degree_out_of_5) / 100
        frappe.model.set_value(cdt, cdn, "degree_based_on_weight", degree_based_on_weight)
    }
}