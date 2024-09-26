frappe.ui.form.on("Designation", {

})

frappe.ui.form.on("Management Skills Details ST", {
    weight(frm,cdt,cdn){
        set_degree_based_on_weight(frm,cdt,cdn)
    },

    target_degree(frm,cdt,cdn){
        set_degree_based_on_weight(frm,cdt,cdn)
    }
})

let set_degree_based_on_weight = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row.weight && row.target_degree) {
        let degree_based_on_weight = (row.weight * row.target_degree) / 100
        frappe.model.set_value(cdt, cdn, "degree_based_on_weight", degree_based_on_weight)
    }
}