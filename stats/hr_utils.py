import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import get_holidays
from stats.stats.report.stats_budget_details.stats_budget_details import get_data
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import today, flt
from frappe.utils import date_diff

def check_if_holiday_between_applied_dates(employee, from_date, to_date, holiday_list=None):
    holidays = get_holidays(employee, from_date, to_date, holiday_list=holiday_list)
    # print(holidays, '-----holiday b/w')
    if holidays > 0:
        return True
    else: return False

def check_employee_in_scholarship(employee, from_date, to_date=None):
    if not to_date:
        to_date=from_date

    scholarship = frappe.qb.DocType('Scholarship Request ST')
    overlapping_scholarship = (
	frappe.qb.from_(scholarship)
            .select(scholarship.name)
            .where(
                (scholarship.employee_no == employee)
                & (scholarship.docstatus < 2)
                & (to_date >= scholarship.scholarship_start_date)
		        & (from_date <= scholarship.scholarship_end_date)
                & (scholarship.acceptance_status == "Accepted")
            )
        ).run(as_dict=True)
    
    # print(overlapping_scholarship, '--overlapping_scholarship')
    if overlapping_scholarship:
        return True
    else: return False

def check_employee_in_training(employee,from_date, to_date):
    if not to_date:
        to_date=from_date

    training = frappe.qb.DocType('Training Request ST')
    overlapping_training = (
	frappe.qb.from_(training)
            .select(training.name)
            .where(
                (training.employee_no == employee)
                & (training.docstatus < 2)
                & (to_date >= training.training_start_date)
		        & (from_date <= training.training_end_date)
                & (training.status == "Accepted")
            )
        ).run(as_dict=True)
    
    # print(overlapping_training, '--overlapping_training')
    if overlapping_training:
        return True
    else: return False

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