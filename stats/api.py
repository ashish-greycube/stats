import frappe
from frappe import _
from frappe.utils import getdate,nowdate,format_duration,cint,get_link_to_form
from dateutil import relativedelta

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_department(doctype, txt, searchfield, start, page_len, filters):
		
		department_list = frappe.get_all("Department", filters={"is_group":0}, fields=["distinct parent_department"], as_list=1)
		unique = tuple(set(department_list))
		# print(unique, '----------ab')
		return unique


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_job_family(doctype, txt, searchfield, start, page_len, filters):
		
		job_family_list = frappe.get_all("Job Family ST", filters={"is_group":0}, fields=["parent_job_family_st"], as_list=1)
		unique = tuple(set(job_family_list))

		return unique

@frappe.whitelist()
def get_supplier_contact(supplier):
	supplier_contact = frappe.db.sql(
		"""
		SELECT
			contact.name
		FROM
			`tabDynamic Link` AS link
		JOIN
			`tabContact` AS contact
		ON
			contact.name=link.parent
		WHERE
			link.link_doctype='Supplier'
			and link.link_name=%s		
		ORDER BY
			contact.creation desc
		limit 1
		""",supplier,as_dict=1,debug=1)	
	if len(supplier_contact) == 0 :
		frappe.msgprint(_("No contact found for supplier: {0}").format(supplier))
		return
	return supplier_contact[0].name

def set_todo_status_in_onboarding_procedures(self, method):
	if not self.is_new():
		doc = frappe.get_doc('Onboarding Procedures ST', {'todo':self.name})
		if doc:
			if self.status == "Closed":
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'date_of_completion', self.date)
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'status', self.status)
				frappe.msgprint(_("Update Status and Date of Completion in {0} 's Onboarding Procedures Row No. {1}")
					.format(doc.parent, doc.idx), alert=1)
			else:
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'status', self.status)
				frappe.db.set_value('Onboarding Procedures ST', doc.name, 'date_of_completion', None)
				frappe.msgprint(_("Update Status in {0} 's Onboarding Procedures Row No. {1}")
					.format(doc.parent, doc.idx), alert=1)

def calculate_years_of_experience(self, method):
	diff = relativedelta.relativedelta(getdate(nowdate()), getdate(self.date_of_joining))

	years = diff.years
	months = diff.months
	days = diff.days

	if self.custom_previous_years_of_experience:
		previous_years = years + self.custom_previous_years_of_experience

		self.custom_current_years_of_experience = str(years) + " years " + str(months) + " months " + str(days) + " days"
		self.custom_total_years_of_experience = str(previous_years) + " years " + str(months) + " months " + str(days) + " days"

@frappe.whitelist()
def set_years_of_experience_at_start_of_every_month():
	employees=frappe.db.get_list('Employee', filters={'status': ['=', 'Active']})
	for employee in employees:
		emp_doc=frappe.get_doc("Employee",employee)
		diff = relativedelta.relativedelta(getdate(nowdate()), getdate(emp_doc.date_of_joining))

		years = diff.years
		months = diff.months
		days = diff.days

		print("in employee")

		if emp_doc.custom_previous_years_of_experience:
			print("yes")
			previous_years = years + emp_doc.custom_previous_years_of_experience
			emp_doc.custom_current_years_of_experience = str(years) + " years " + str(months) + " months " + str(days) + " days"
			emp_doc.custom_total_years_of_experience = str(previous_years) + " years " + str(months) + " months " + str(days) + " days"
			emp_doc.add_comment("Comment", text='Employee experience added till {0}'.format(nowdate()))
			print("added")
			emp_doc.save(ignore_permissions=True)

@frappe.whitelist()
def fetch_employee_per_diem_amount(employee,no_of_days):
	employee_grade = frappe.db.get_value("Employee",employee,"grade")
	if employee_grade:
		employee_per_diem_amount = frappe.db.get_value("Employee Grade",employee_grade,"custom_per_diem")
		if employee_per_diem_amount == 0:
			frappe.throw(_("Please set per diem amount for employee in employee grade {0}").format(get_link_to_form("Employee Grade",employee_grade)))
		total_employee_amount_for_trip = employee_per_diem_amount * cint(no_of_days)
		return total_employee_amount_for_trip


@frappe.whitelist()
def set_no_of_business_trip_days_available_at_start_of_every_year():
	employees=frappe.db.get_list('Employee', filters={'status': ['=', 'Active']})
	for employee in employees:
		emp_doc=frappe.get_doc("Employee",employee)
		custom_contract_type=emp_doc.custom_contract_type
		no_of_allowed_business_trip_days = frappe.db.get_value('Contract Type ST', custom_contract_type, 'no_of_allowed_business_trip_days')
		emp_doc.custom_no_of_business_trip_days_remaining=no_of_allowed_business_trip_days
		emp_doc.add_comment("Comment", text='No of business trip days are set to {0} on {1} by system.'.format(no_of_allowed_business_trip_days,nowdate()))
		emp_doc.save(ignore_permissions=True)

@frappe.whitelist()
def check_leave_is_not_in_business_days(self,method):
		business_trip_request_details=	frappe.db.sql(
					"""
					select
						name
					from `tabBusiness Trip Request ST`
					where employee_no = %(employee)s and docstatus < 2 and status in ('Pending', 'Approved')
					and (
					( business_trip_start_date <= %(from_date)s and business_trip_end_date >= %(from_date)s )
					or ( business_trip_start_date >= %(from_date)s and business_trip_end_date <= %(to_date)s )
					or ( business_trip_start_date <= %(to_date)s and business_trip_end_date >= %(to_date)s )
					)
					""",
					{
						"employee": self.employee,
						"from_date": self.from_date,
						"to_date": self.to_date,
					},
					as_dict=1,debug=1
				)
		print('business_trip_request_details',business_trip_request_details)
		if len(business_trip_request_details)>0:
			business_trip_names=",".join(i.name for i in business_trip_request_details)
			frappe.throw(_("You have business trip <b>{0}</b> during your leave applicatino days. It is not allowed.").format(business_trip_names))
			
				
def create_budget(cost_center, fiscal_year, budget_expense_account, net_balance):
	print('create_budget')

	new_budget = frappe.new_doc('Budget')
	new_budget.cost_center = cost_center
	new_budget.fiscal_year = fiscal_year
	row = new_budget.append('accounts',{})
	row.account = budget_expense_account
	row.budget_amount = net_balance

	new_budget.submit()
	frappe.msgprint(_("Budget {0} is created."
		.format(get_link_to_form('Budget', new_budget.name))), alert=True)
	print(new_budget.name ,'------new_budget')

	return new_budget.name

@frappe.whitelist()
def set_scholarship_status_closed():
	open_scholarship_list = frappe.db.get_all("Scholarship ST",
										   filters = {"docstatus":1,"status":"Open"},
										   fields=["name","apply_end_date","status"])
	for scholarship in open_scholarship_list:
		if scholarship.apply_end_date == getdate(nowdate()):
			scholarship_doc = frappe.get_doc("Scholarship ST",scholarship.name)
			scholarship_doc.status = "Closed"
			scholarship_doc.add_comment("Comment", text='Scholarship status is Closed on {0} by system.'.format(nowdate()))
			scholarship_doc.save(ignore_permissions = True)

def create_salary_component(name,abbreviation,type):
	salary_component_doc = frappe.new_doc("Salary Component")
	salary_component_doc.salary_component = name
	salary_component_doc.salary_component_abbr = abbreviation
	salary_component_doc.type = "Deduction"
	salary_component_doc.run_method('set_missing_values')
	salary_component_doc.save(ignore_permissions=True)