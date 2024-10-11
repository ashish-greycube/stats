import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import get_holidays
from stats.stats.report.stats_budget_details.stats_budget_details import get_data
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import today, flt
from frappe.utils import date_diff

def check_if_holiday_between_applied_dates(from_date, to_date,employee=None, holiday_list=None):
    number_of_days = date_diff(to_date, from_date)
    number_of_days = flt(number_of_days) - flt(	get_holidays(employee, from_date, to_date, holiday_list=holiday_list))
    return number_of_days

def check_employee_in_scholarship(employee,from_date, to_date):
    scholarship = frappe.db.exists("Scholarship Request ST", {"employee_no": employee, 
                                                              "transaction_date": ["between", [from_date, to_date]],
                                                              "acceptance_status": "Accepted"})
    
    # print(scholarship, '--scholarship')
    return scholarship

def check_employee_in_training(employee,from_date, to_date):
    training = frappe.db.exists("Training Request ST", {"employee_no":employee,
                                                        "date":["between", [from_date, to_date]],
                                                        "status": ["in", ["Accepted", "Finished"]]})
    # print(training, '---training')
    return training


def check_available_amount_for_budget(budget_account,cost_center):
    fiscal_year = get_fiscal_year(today())[0]
    filters=frappe._dict({'fiscal_year': fiscal_year, 'cost_center': cost_center, 'account': budget_account})
    budget = get_data(filters)

    if len(budget) > 0:
        return budget[0].get("available")
    else:
        return


def get_latest_total_monthly_salary_of_employee(employee):
    employee_monthly_salary = frappe.db.get_all("Salary Structure Assignment", filters={"employee":employee, "from_date": ["<=", today()]}, 
                                                fields=["base"],
                                                order_by= "from_date desc",
                                                limit=1)
    
    print(employee_monthly_salary, '--employee_monthly_salary')
    
    if len(employee_monthly_salary) > 0:
        return employee_monthly_salary[0].base
    else: 
        return