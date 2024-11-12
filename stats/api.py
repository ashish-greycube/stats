import frappe
from frappe import _
from frappe.utils import add_to_date,get_datetime,getdate,nowdate,format_duration,cint,get_link_to_form,flt,add_years,time_diff_in_hours,now,rounded,flt,get_time,time_diff_in_seconds
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
				
def set_employee_company_email(self, method):
	if self.reference_type == "Employee Onboarding ST":
		if self.custom_create_company_email == 1 and self.custom_company_email and self.status == "Open":
			job_offer_reference = frappe.db.get_value("Employee Onboarding ST", self.reference_name, 'job_offer_reference')
			if job_offer_reference:
				employee = frappe.get_doc("Employee", {'custom_job_offer_reference': job_offer_reference})
				employee.company_email = self.custom_company_email
				employee.save(ignore_permissions=True)


def calculate_years_of_experience(self, method):
	diff = relativedelta.relativedelta(getdate(nowdate()), getdate(self.date_of_joining))

	years = diff.years
	months = diff.months
	days = diff.days

	if self.custom_previous_years_of_experience:
		previous_years = years + self.custom_previous_years_of_experience

		self.custom_current_years_of_experience = str(years) + " years " + str(months) + " months " + str(days) + " days"
		self.custom_total_years_of_experience = str(previous_years) + " years " + str(months) + " months " + str(days) + " days"

def set_employee_in_man_power_planning_for_job_no(self, method):
	if self.custom_job_no and not self.is_new():
		job_no = frappe.get_doc("MP Jobs Details ST",{"job_no":self.custom_job_no})
		if not job_no.employee_no:
			frappe.db.set_value(job_no.doctype, job_no.name, "employee_no", self.name)
			frappe.msgprint(_("set Employee {0} in Job No {1}").format(self.name, self.custom_job_no), alert=True)

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

def check_monthly_salary_component_offer_term(self,method):
    if self.custom_is_monthly_salary_component == 1:
        offer_term_list = frappe.db.get_all("Offer Term",
                                      filters={"custom_is_monthly_salary_component":1, "name": ["!=", self.name]},
                                      fields=["name"])
        if len(offer_term_list)>0:
                frappe.throw(_("Offer Term <b>'{0}'</b> is already set as Monthly Salary Component".format(offer_term_list[0].name)))

def create_salary_structure_assignment(self, method):
	if self.custom_employee_contract_ref:
		total_monthly_salary = 0
		if len(self.earnings)>0:
			for ear in self.earnings:
				total_monthly_salary = total_monthly_salary + ear.amount

		# amount = frappe.db.get_value("Employee Contract ST", self.custom_employee_contract_ref, "total_monthly_salary")
		assignment = frappe.new_doc("Salary Structure Assignment")
		assignment.employee = self.custom_employee_no
		assignment.salary_structure = self.name
		assignment.from_date = self.custom_contract_start_date
		assignment.base = total_monthly_salary

		assignment.save(ignore_permissions=True)
		frappe.msgprint(_("Salary Structure Assignment {0} created." .format(get_link_to_form('Salary Structure Assignment', assignment.name))), alert=True)
		assignment.submit()

def get_monthly_salary_from_job_offer(job_offer):
	doc = frappe.get_doc("Job Offer ST", job_offer)

	if doc:
		monthly_salary = 0
		if len(doc.offer_details) > 0:
			for offer in doc.offer_details:
				monthly_salary_component = frappe.db.get_value('Offer Term', offer.offer_term, 'custom_is_monthly_salary_component')
				if monthly_salary_component == 1:
					monthly_salary = offer.value

	return monthly_salary

def get_base_amount_from_salary_structure_assignment(employee):
	base = frappe.db.get_value("Salary Structure Assignment", {"employee":employee, "docstatus":1}, 'base')
	if base == None:
		frappe.throw(_("No Base Amount Found"))
	else:
		return base

def validate_weight_and_set_degree_based_on_weight(self, method):
	set_degree_based_on_weight(self.custom_management_skills)
	validate_weight(self.custom_management_skills)

def set_degree_based_on_weight(details):
	if len(details)>0:
		for row in details:
			if row.weight and row.target_degree:
					row.degree_based_on_weight = flt((row.weight * row.target_degree) / 100,2)

def validate_weight(details):
	if len(details)>0:
		total_weight = 0
		for row in details:
			if row.weight:
				total_weight = total_weight + row.weight
			else:
				frappe.throw(_("Row #{0}: Weight cannot be 0").format(row.idx))
		if total_weight != 100:
			frappe.throw(_("Total of weight must be 100"))

def calculate_actual_degree_based_on_weight(details):
	if len(details)>0:
		for row in details:
			if row.actual_degree and row.weight:
				row.actual_degree_based_on_weight = flt((row.actual_degree * row.weight) / 100, 2)

@frappe.whitelist()
def create_employee_evaluation_yearly_and_half_yearly():
	stats_settings_doc = frappe.get_doc("Stats Settings ST")
	today = getdate(nowdate())
	# today = getdate("2026-12-31")
	print(today,"today",type(today),"stats_settings_doc",stats_settings_doc.annual_creation_date,type(getdate(stats_settings_doc.annual_creation_date)))
	if today == getdate(stats_settings_doc.annual_creation_date):
		all_active_employee_list = frappe.db.get_all("Employee",filters={"status":"Active","custom_test_period_completed":"Yes"},fields=["name"])

		if len(all_active_employee_list)>0:
			for employee in all_active_employee_list:
				employee_doc = frappe.get_doc("Employee",employee.name)
				employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
				if today == getdate(stats_settings_doc.annual_creation_date):
					employee_evaluation_doc.employee_no = employee.name
					employee_evaluation_doc.creation_date = stats_settings_doc.annual_creation_date
					employee_evaluation_doc.evaluation_type = "Yearly"
					employee_evaluation_doc.evaluation_from = stats_settings_doc.annual_evaluation_from
					employee_evaluation_doc.evaluation_to = stats_settings_doc.annual_evaluation_to

				elif today == getdate(stats_settings_doc.half_yearly_creation_date):
					employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
					employee_evaluation_doc.employee_no = employee.name
					employee_evaluation_doc.creation_date = stats_settings_doc.half_yearly_creation_date
					employee_evaluation_doc.evaluation_type = "Half Yearly"
					employee_evaluation_doc.evaluation_from = stats_settings_doc.half_yearly_evaluation_from
					employee_evaluation_doc.evaluation_to = stats_settings_doc.half_yearly_evaluation_to
				
				employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
												filters={"employee_no":employee.name,"docstatus":1},
												fields=["name"])
				if len(employee_personal_goal)>0:
					employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
					if len(employee_personal_goal_doc.personal_goals)>0:
						for row in employee_personal_goal_doc.personal_goals:
							personal_goal = employee_evaluation_doc.append("employee_personal_goals",{})
							personal_goal.goals = row.goals
							personal_goal.weight = row.weight
							personal_goal.target_degree = row.target_degree

				if employee_doc.grade:
					evaluation_template = frappe.db.get_all("Employee Evaluation Template ST",
												filters={"grade":employee_doc.grade},
												fields=["name"])
					if len(evaluation_template)>0:
						evaluation_template_doc = frappe.get_doc("Employee Evaluation Template ST",evaluation_template[0].name)
						if len(evaluation_template_doc.job_goals)>0:
							for row in evaluation_template_doc.job_goals:
								job_goal = employee_evaluation_doc.append("employee_job_goals",{})
								job_goal.goals = row.goals
								job_goal.weight = row.weight
								job_goal.uom = row.uom
								job_goal.target_degree = row.target_degree

				if employee_doc.designation:
					designation_doc = frappe.get_doc("Designation",employee_doc.designation)
					if len(designation_doc.custom_management_skills)>0:
						for row in designation_doc.custom_management_skills:
							management_skill = employee_evaluation_doc.append("employee_management_skills",{})
							management_skill.skill = row.skill
							management_skill.skill_description = row.skill_description
							management_skill.weight = row.weight
							management_skill.target_degree = row.target_degree

				employee_evaluation_doc.save(ignore_permissions=True)
				employee_evaluation_doc.add_comment("Comment",text="Created by system on {0}".format(nowdate()))

			if today == getdate(stats_settings_doc.annual_creation_date):
				next_yearly_evaluation_date = add_years(stats_settings_doc.annual_creation_date, 1)
				next_yearly_evaluation_from_date = add_years(stats_settings_doc.annual_evaluation_from, 1)
				next_yearly_evaluation_to_date = add_years(stats_settings_doc.annual_evaluation_to, 1)

				print(next_yearly_evaluation_date,"next_yearly_evaluation_date","----",next_yearly_evaluation_from_date,'next_yearly_evaluation_from_date',"----",next_yearly_evaluation_to_date,"next_yearly_evaluation_to_date")
				stats_settings_doc.annual_creation_date = next_yearly_evaluation_date
				stats_settings_doc.annual_evaluation_from = next_yearly_evaluation_from_date
				stats_settings_doc.annual_evaluation_to = next_yearly_evaluation_to_date
				stats_settings_doc.add_comment("Comment",text="Annual Evaluation Default Dates are updated on {0}".format(nowdate()))
				stats_settings_doc.save(ignore_permissions=True)
				
			elif today == getdate(stats_settings_doc.half_yearly_creation_date):
				next_half_yearly_evaluation_date = add_years(stats_settings_doc.half_yearly_creation_date, 1)
				next_half_yearly_evaluation_from_date = add_years(stats_settings_doc.half_yearly_evaluation_from, 1)
				next_half_yearly_evaluation_to_date = add_years(stats_settings_doc.half_yearly_evaluation_to, 1)

				print(next_half_yearly_evaluation_date,"next_half_yearly_evaluation_date","----",next_half_yearly_evaluation_from_date,'next_half_yearly_evaluation_from_date',"----",next_half_yearly_evaluation_to_date,"next_yearly_evaluation_to_date")
				stats_settings_doc.half_yearly_creation_date = next_half_yearly_evaluation_date
				stats_settings_doc.half_yearly_evaluation_from = next_half_yearly_evaluation_from_date
				stats_settings_doc.half_yearly_evaluation_to = next_half_yearly_evaluation_to_date
				stats_settings_doc.add_comment("Comment",text="Half-Yearly Evaluation Default Dates are updated on {0}".format(nowdate()))
				stats_settings_doc.save(ignore_permissions=True)

@frappe.whitelist()
def create_employee_evaluation_based_on_employee_contract():
	today = getdate(nowdate())
	# today = getdate("2024-12-26")
	employee_contract_list = frappe.db.get_all("Employee Contract ST",
											filters={"docstatus":1},
											or_filters={"test_period_end_date":today,"end_of_new_test_period":today},
											fields=["name"])
	default_template_for_test_period = frappe.db.get_single_value("Stats Settings ST","default_evaluation_template_for_test_period")
	if len(employee_contract_list)>0:
		for contract in employee_contract_list:
			print(contract,"--")
			employee_contract_doc = frappe.get_doc("Employee Contract ST",contract.name)
			if employee_contract_doc.end_of_new_test_period or employee_contract_doc.test_period_end_date:
				employee_evaluation_doc = frappe.new_doc("Employee Evaluation ST")
				employee_evaluation_doc.employee_no = employee_contract_doc.employee_no
				employee_evaluation_doc.creation_date = today
				employee_evaluation_doc.evaluation_type = "Test Period"
				employee_evaluation_doc.employee_contract_reference = employee_contract_doc.name

				if employee_contract_doc.end_of_new_test_period == today:
					employee_evaluation_doc.evaluation_from = employee_contract_doc.test_period_end_date
					employee_evaluation_doc.evaluation_to = employee_contract_doc.end_of_new_test_period

				elif employee_contract_doc.test_period_end_date == today:
					employee_evaluation_doc.evaluation_from = employee_contract_doc.contract_start_date
					employee_evaluation_doc.evaluation_to = employee_contract_doc.test_period_end_date
				
				employee_grade = frappe.db.get_value("Employee",employee_contract_doc.employee_no,"grade")
				employee_designation = frappe.db.get_value("Employee",employee_contract_doc.employee_no,"designation")
				employee_personal_goal = frappe.db.get_all("Employee Personal Goals ST",
											filters={"employee_no":employee_contract_doc.employee_no,"docstatus":1},
											fields=["name"])
				if len(employee_personal_goal)>0:
					employee_personal_goal_doc = frappe.get_doc("Employee Personal Goals ST",employee_personal_goal[0].name)
					if len(employee_personal_goal_doc.personal_goals)>0:
						for row in employee_personal_goal_doc.personal_goals:
							personal_goal = employee_evaluation_doc.append("employee_personal_goals",{})
							personal_goal.goals = row.goals
							personal_goal.weight = row.weight
							personal_goal.target_degree = row.target_degree

				if employee_grade:
					evaluation_template = frappe.db.get_all("Employee Evaluation Template ST",
												filters={"grade":employee_grade},
												fields=["name"])
					if len(evaluation_template)>0:
						evaluation_template_doc = frappe.get_doc("Employee Evaluation Template ST",evaluation_template[0].name)
						if len(evaluation_template_doc.job_goals)>0:
							for row in evaluation_template_doc.job_goals:
								job_goal = employee_evaluation_doc.append("employee_job_goals",{})
								job_goal.goals = row.goals
								job_goal.weight = row.weight
								job_goal.uom = row.uom
								job_goal.target_degree = row.target_degree
				if default_template_for_test_period:
					evaluation_template_doc = frappe.get_doc("Employee Evaluation Template ST",default_template_for_test_period)
					if len(evaluation_template_doc.job_goals)>0:
						for row in evaluation_template_doc.job_goals:
							job_goal = employee_evaluation_doc.append("employee_job_goals",{})
							job_goal.goals = row.goals
							job_goal.weight = row.weight
							job_goal.uom = row.uom
							job_goal.target_degree = row.target_degree

				if employee_designation:
					designation_doc = frappe.get_doc("Designation",employee_designation)
					if len(designation_doc.custom_management_skills)>0:
						for row in designation_doc.custom_management_skills:
							management_skill = employee_evaluation_doc.append("employee_management_skills",{})
							management_skill.skill = row.skill
							management_skill.skill_description = row.skill_description
							management_skill.weight = row.weight
							management_skill.target_degree = row.target_degree

				employee_evaluation_doc.save(ignore_permissions=True)
				employee_evaluation_doc.add_comment("Comment",text="Created by system on {0}".format(nowdate()))

def calculate_extra_working_hours(self,method):
    shift_start_time = frappe.db.get_value("Shift Type",self.shift,"start_time")
    shift_end_time = frappe.db.get_value("Shift Type",self.shift,"end_time")

    actual_working_hours = time_diff_in_hours(shift_end_time, shift_start_time)
    employee_working_hours = self.working_hours

    # rounded_employee_working_hours = rounded(employee_working_hours - actual_working_hours, 0)
    if employee_working_hours and (employee_working_hours > 0):
        employee_working_hours_in_minutes = employee_working_hours * 60
        self.custom_actual_working_hours = employee_working_hours_in_minutes
        if self.custom_net_working_hours == 0:
            self.custom_net_working_hours = self.custom_actual_working_hours

        if employee_working_hours > actual_working_hours:
            int_hours, dec_min = divmod(employee_working_hours - actual_working_hours, 1)
            extra_min = cint(rounded(dec_min * 60,0)) 
            int_hours = cint(int_hours)
            total_extra_min = (int_hours*60) + extra_min
            self.custom_extra_hours = total_extra_min
    if self.late_entry == 1:
        late_entry_duration = time_diff_in_seconds(str((self.in_time).time()),str(get_time(str(shift_start_time))))
        self.custom_actual_delay = cint(rounded(late_entry_duration/60,0))
    
    if self.early_exit == 1:
        early_exit_duration = time_diff_in_seconds(str(get_time(str(shift_end_time))),str((self.out_time).time()))
        self.custom_actual_early = cint(rounded(early_exit_duration/60,0))
    
    if not self.custom_attendance_type:
        if self.status:
            self.custom_attendance_type = self.status
        
    if self.custom_net_working_hours:
        self.custom_difference_in_working_hours = self.custom_net_working_hours - self.custom_actual_working_hours

def validate_duplicate_record_for_employee_checkin(self):
		# employee_checkin = frappe.db.get_all("Employee Checkin",
		# 							   filters={"employee":self.employee,"log_type":self.log_type,"time":self.time},
		# 							   fields=["name","time"])
		employee_checkin = frappe.db.exists("Employee Checkin",{"employee":self.employee,"log_type":self.log_type,"time":self.time})
		
		print(employee_checkin,"-----")
		# if len(employee_checkin)>0:
		if employee_checkin != None and employee_checkin != self.name:
			print("Done")
			frappe.throw(_("This employee already has a employee checkin with the same date and attendance type <br><b>{0}</b>").format(get_link_to_form("Employee Checkin",ele.name)))

def set_last_sync_of_checkin_in_all_shift_type():
	shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
	for shift in shift_list:
		shift_type_doc = frappe.get_doc("Shift Type",shift)
		shift_type_doc.last_sync_of_checkin = now()
		shift_type_doc.add_comment("Comment",text="Last Sync of Checkin is updated by system on {0}".format(now()))
		shift_type_doc.save(ignore_permissions=True)

def set_last_sync_of_checkin_on_save_of_employee_checkin(self,method):
	if not (self.skip_auto_attendance or not self.shift):
		print("IN FUNC ----------------------------")
		latest_checkin = frappe.get_last_doc("Employee Checkin", filters={"shift": self.shift}, order_by="time desc")
		current_last_sync_of_checkin_in_shift = frappe.db.get_value("Shift Type", self.shift, "last_sync_of_checkin")
		print(latest_checkin.time,"latest_checkin.time-------",type(latest_checkin.time),current_last_sync_of_checkin_in_shift,"current_last_sync_of_checkin_in_shift",type(current_last_sync_of_checkin_in_shift))
		if latest_checkin.time > current_last_sync_of_checkin_in_shift:
			print("Valid -----")
			frappe.db.set_value("Shift Type", self.shift, "last_sync_of_checkin", latest_checkin.time)

def create_employee_checkin_checkout_for_training():
	today = nowdate()
	# training_request_list = frappe.db.get_all("Training Request ST",
	# 									   filters={"employee_checkin_required":"Yes","employee_checkout_required":"Yes"},
	# 									   or_filters={'training_start_date':['between',[filter__from_date,filter__to_date]],
    #                                           'all_line_cast_off':['between',[filter__from_date,filter__to_date]] },)



def get_non_working_days(employee, payroll_end_date) -> float:
	filters = {
		"docstatus": 1,
		"status": "On Leave",
		"employee": employee,
		"attendance_date": ("<=", get_datetime(payroll_end_date)),
	}

	# if status == "On Leave":
	lwp_leave_types = frappe.get_all("Leave Type", filters={"is_lwp": 1}, pluck="name")
	filters["leave_type"] = ("IN", lwp_leave_types)

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(*) as total_lwp"])
	return record[0].total_lwp if len(record) else 0

@frappe.whitelist()
def calculate_lwp_dedution(payroll_entry):
	payroll_entry = frappe.get_doc("Payroll Entry", payroll_entry)
	previous_month_last_date = add_to_date(payroll_entry.start_date,days=-1)

	print(previous_month_last_date, '----------previous_month_last_date-----------')

	emp_dedution_list = []
	for emp in payroll_entry.employees:
		total_lwp = get_non_working_days(emp.employee, previous_month_last_date)
		print(total_lwp, '--total_lwp')
	
		emp_dedution_details = {}
		
		if total_lwp > 0:
			salary_assignment = frappe.db.get_all("Salary Structure Assignment", 
								  fields=["name", "salary_structure"], filters={"from_date": ["<=", nowdate()], "employee":emp.employee}, 
								  order_by = "from_date desc", limit=1)
			print(salary_assignment[0].name, '--salary_assignment')
			if len(salary_assignment) > 0:
				ss = frappe.get_doc("Salary Structure", salary_assignment[0].salary_structure)
				
				total_lwp_deduction = 0
				for ear in ss.earnings:
					deduction_component = frappe.db.get_value("Salary Component", ear.salary_component, 'custom_consider_for_deduction_calculation')
					if deduction_component == 1:
						total_lwp_deduction = total_lwp_deduction + ((ear.amount)/30) * total_lwp

				emp_dedution_details['employee'] = emp.employee
				emp_dedution_details['deduction'] = total_lwp_deduction
				print(total_lwp_deduction, '---total_lwp_deduction')

				emp_dedution_list.append(emp_dedution_details)

		else:	
			emp_dedution_details['employee'] = emp.employee
			emp_dedution_details['deduction'] = 0

			emp_dedution_list.append(emp_dedution_details)
				
	return emp_dedution_list


def create_additonal_salary_for_deduction(self, method):

	lwp_deduction_component = frappe.db.get_single_value('Stats Settings ST', 'lwpabsent_deduction_component')

	for emp in self.employees:
		if emp.custom_lwp_deduction > 0:
			additional_salary = frappe.new_doc("Additional Salary")
			additional_salary.employee = emp.employee
			additional_salary.payroll_date = self.start_date
			additional_salary.salary_component =  lwp_deduction_component
			additional_salary.overwrite_salary_structure_amount = 1
			additional_salary.amount = emp.custom_lwp_deduction
			additional_salary.save(ignore_permissions=True)
			frappe.msgprint(_("Additional Salary {0} Created for Employee {1}.").format(additional_salary.name, emp.employee), alert=1)
			additional_salary.submit()