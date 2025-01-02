frappe.ui.form.on("Purchase Order", {
    onload(frm) {
        frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['employee_name', 'department', 'custom_sub_department'])
            .then(r => {
                let values = r.message;
                frm.set_value('custom_created_by', values.employee_name)
                frm.set_value('custom_main_department', values.department)
                frm.set_value('custom_sub_department', values.custom_sub_department)
            })
    },

    custom_supply_period_option(frm){
        calculate_contract_end_date(frm)
    },

    custom_supply_period(frm){
        calculate_contract_end_date(frm)
    },

    custom_contrcat_start_date(frm){
        calculate_contract_end_date(frm)
    }
})

let calculate_contract_end_date = function(frm){

    if (frm.doc.custom_supply_period){
        let supply_period = frm.doc.custom_supply_period
        if (frm.doc.custom_contrcat_start_date){
            let statr_date = frm.doc.custom_contrcat_start_date

            if (frm.doc.custom_supply_period_option == "Day"){
                let end_date = frappe.datetime.add_days(statr_date, supply_period)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Week"){
                let week_days = supply_period * 7
                let end_date = frappe.datetime.add_days(statr_date, week_days)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Month"){
                let end_date = frappe.datetime.add_months(statr_date, supply_period)
                frm.set_value("custom_contract_end_date",end_date)
            }

            if (frm.doc.custom_supply_period_option == "Year"){
                let end_date = frappe.datetime.add_months(statr_date, supply_period*12)
                frm.set_value("custom_contract_end_date",end_date)
            }
        }
    }
}