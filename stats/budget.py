import frappe
from frappe import _



def get_budget_account_details(budget_cost_center,budget_expense_account,fiscal_year):
    filters={
        'budget_cost_center':budget_cost_center,
        'budget_expense_account':budget_expense_account,
        'fiscal_year':fiscal_year
        }
    budget_detials = frappe.db.sql(
        """
            select
                            b.cost_center,
                            gl.account,
                            ba.budget_amount as approved,
                            sum(gl.debit)-sum(gl.credit) as used,
                            ba.budget_amount-sum(gl.debit)-sum(gl.credit) as available,
                            gl.fiscal_year
            from
                            `tabGL Entry` gl,
                            `tabBudget Account` ba,
                            `tabBudget` b
            where
                            b.name = ba.parent
                and b.docstatus = 1
                and ba.account = gl.account
                and b.cost_center = gl.cost_center
                and gl.fiscal_year = %(fiscal_year)s
                and b.cost_center =  %(budget_cost_center)s
                and gl.account = %(budget_expense_account)s
            group by
                gl.name
        """,filters,as_dict=1,debug=1)
    
    if len(budget_detials)>0:
        return budget_detials[0]
    else:
        return None


