frappe.ui.form.on("Material Request", {
    refresh(frm){
        if(frm.doc.docstatus==1 && frm.doc.custom_request_classification=='General Competition'){
            frm.add_custom_button(
				__("Create Purchase Comittee"),
				function () {
					frappe.model.open_mapped_doc({
						method: "stats.api.create_purchase_comittee",
						frm: frm,
					});
				});
        }
    }
})