frappe.ui.form.on("Leave Application", {
    refresh: function (frm) {
		if (frm.doc.status == 'Approved' && frm.doc.docstatus == 1) {
			frm.add_custom_button(
				__("Leave Change Request"),
				function () {
					frappe.model.open_mapped_doc({
						method: "stats.api.make_leave_application_change_request",
						frm: frm,
					});
				});
		}
	},
	employee: function(frm){
		frappe.db.get_value('Employee', frm.doc.employee, 'custom_country')
			.then(r => {
				console.log(r.message.custom_country, "=========custom_country")
				if(r.message.custom_country == "Saudi Arabia"){
					frm.set_df_property('custom_exit_entry_required', 'hidden', 0)
					frm.set_df_property('custom_ticket_required', 'hidden', 1)
				}
				else if(r.message.custom_country){
					frm.set_df_property('custom_exit_entry_required', 'hidden', 1)
					frm.set_df_property('custom_ticket_required', 'hidden', 0)
				}
				else{
					frm.set_df_property('custom_exit_entry_required', 'hidden', 1)
					frm.set_df_property('custom_ticket_required', 'hidden', 1)
				}
			
			
			})
	}
})