// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Offer ST", {
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
	refresh: function (frm) {
		if (frm.doc.status == 'Accepted') {
			frm.set_df_property('date_of_birth', 'reqd', 1)
			frm.add_custom_button(
				__("Create Employee"),
				function () {
					frappe.model.open_mapped_doc({
						method: "stats.stats.doctype.job_offer_st.job_offer_st.make_employee",
						frm: frm,
					});
				});
		}
	},
	job_application_reference: function(frm){
		if(frm.is_new() && frm.doc.contract_type){
			fill_salary_tables(frm)
		}
	},
	contract_type: function(frm) {
		if(frm.is_new()){
			fill_salary_tables(frm)
		}
		// if (frm.is_new()) {
		// 	frm.set_value("earning", "");
		// 	frm.set_value("deduction", "");
		// 	if (frm.doc.contract_type) {
		// 		frappe.call({
		// 			method: "stats.stats.doctype.job_offer_st.job_offer_st.fetch_salary_tables_from_contract_type",
		// 			args: {
		// 				parent: frm.doc.contract_type,
		// 				parenttype: "Contract Type ST",
		// 			},
		// 			callback: function (r) {
		// 				if (r.message[0]) {
		// 					r.message[0].forEach((e) => {
		// 						frm.add_child("earning", e);
		// 					});
		// 					refresh_field("earning");
		// 				}
		// 				if (r.message[1]) {
		// 					r.message[1].forEach((d) => {
		// 						frm.add_child("deduction", d);
		// 					});
		// 					refresh_field("deduction");
		// 				}
		// 			},
		// 		});
		// 	}
		// }
		
	}
});

frappe.ui.form.on("Job Offer Details ST", {
	// offer_term: function (frm, cdt, cdn) {
	// 	let row = locals[cdt][cdn]
	// 	frappe.db.get_value('Offer Term', row.offer_term, 'custom_is_monthly_salary_component')
	// 	.then(r => {
	// 		console.log(r.message.custom_is_monthly_salary_component, '---r.message.custom_is_monthly_salary_component == 1')
	// 		if(r.message.custom_is_monthly_salary_component == 1){
	// 			console.log("hello")
	// 			frappe.db.get_value('MP Jobs Details ST', frm.doc.job_title , 'salary')
	// 			.then(value => {
	// 				console.log(value, '---value')
	// 				// let values = value.message;
	// 				// console.log(values.salary)
	// 					console.log(value.salary, '---value.salary')
	// 					// frappe.model.set_value(cdt, cdn, 'value', value.salary)
	// 			})
	// 		}
	// 	})
	// },
	value: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.offer_term) {
			frappe.db.get_value('Offer Term', row.offer_term, 'custom_is_monthly_salary_component')
				.then(r => {
					if(r.message.custom_is_monthly_salary_component == 1){
						if(frm.is_new() && frm.doc.contract_type){
							fill_salary_tables(frm)
						}
					} 
				})
		}
	}
})

let fill_salary_tables = function(frm) {
	frm.call("fill_salary_tables");
	// frm.save()
}