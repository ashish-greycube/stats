// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Contract ST", {
	job_offer_reference: function (frm) {
		frm.set_value("earning", "");
        frm.set_value("deduction", "");
		if (frm.doc.job_offer_reference) {
			frappe.call({
				method: "stats.stats.doctype.employee_contract_st.employee_contract_st.get_salary_details",
				args: {
					parent: frm.doc.job_offer_reference,
					parenttype: "Job Offer ST",
				},
				callback: function (r) {
					if (r.message[0]) {
						r.message[0].forEach((e) => {
							frm.add_child("earning", e);
						});
						refresh_field("earning");
					}
                    if (r.message[1]) {
						r.message[1].forEach((d) => {
							frm.add_child("deduction", d);
						});
						refresh_field("deduction");
					}
				},
			});
		}
	},
    contract_start_date: function(frm){
        if(frm.doc.contract_start_date){
            let trial_period = frappe.datetime.add_months(frm.doc.contract_start_date, 3)
            frm.set_value('trial_period_end_date', trial_period)
        }
        else{
            frm.set_value('trial_period_end_date', '')
        }
    },
    test_period_renewed: function(frm){
        if(frm.doc.test_period_renewed == "Yes"){
            let renew_trial_period = frappe.datetime.add_months(frm.doc.trial_period_end_date, 3)
            frm.set_value('end_of_new_test_period', renew_trial_period)
        }
        else{
            frm.set_value('end_of_new_test_period', '')
        }
    }
});
