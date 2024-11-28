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
        if(frm.doc.docstatus==1 && frm.doc.custom_request_classification=='General Competition' && (frm.doc.custom_purchasing_committee_status!='Finished')){
            frm.remove_custom_button('Purchase Order', 'Create');
        }        
    },

    onload(frm) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
            .then(r => {
                let values = r.message;
                frm.set_value('custom_created_by', values.employee_name)
                frm.set_value('custom_main_department', values.department)
                frm.set_value('custom_sub_department', values.custom_sub_department)
            })
    },

    custom_request_classification(frm){
        if (frm.doc.custom_request_classification == "General Competition"){
            frm.set_value("custom_purchasing_committee_status","Pending")
        }
    },
})