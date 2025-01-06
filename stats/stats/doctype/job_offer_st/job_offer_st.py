# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.model.mapper import get_mapped_doc
from stats.api import get_monthly_salary_from_job_offer

class JobOfferST(Document):
	# def before_save(self):
	# 	self.calculate_salary_earnings_and_deduction()

	def validate(self):
		self.validate_basic_salary_amount()
		# self.fetch_salary_tables_from_contract_type()
		# self.validate_offer_term_details()
		# self.validate_duplicate_entry_for_offer_term_with_monthly_salary_component()
		# self.validate_value_in_offer_details()
		# self.calculate_salary_earnings_and_deduction()
		# self.validate_total_monthly_salary_earnings_and_deductions()

	def validate_basic_salary_amount(self):
		if self.basic_salary_amount < 1:
			frappe.throw("Basic Salary Component is Mandatory field.")

		grade_doc = frappe.get_doc("Employee Grade", self.grade)

		if self.basic_salary_amount > grade_doc.custom_max_basic_amount:
			frappe.throw(_("Basic Salary Amount Cann't be More Than {0} Grade Maximum Basic Amount.").format(grade_doc.custom_max_basic_amount))
		
		if self.basic_salary_amount < grade_doc.custom_minimum_basic_amount:
			frappe.throw(_("Basic Salary Amount Cann't be Less Than {0} Grade Manimum Basic Amount.").format(grade_doc.custom_minimum_basic_amount))

	def validate_offer_term_details(self):
		offer_term_in_offer_details_list = []
		if len(self.offer_details) > 0:
			offer_term_with_monthly_salary_component = frappe.db.exists("Offer Term", {"custom_is_monthly_salary_component": 1})
			if offer_term_with_monthly_salary_component:
				for row in self.offer_details:
					offer_term_in_offer_details_list.append(row.offer_term)
				if offer_term_with_monthly_salary_component not in offer_term_in_offer_details_list:
					frappe.throw(_("There must be one offer term with monthly salary component "))

	def validate_duplicate_entry_for_offer_term_with_monthly_salary_component(self):
		offer_term_with_monthly_salary_component = frappe.db.exists("Offer Term", {"custom_is_monthly_salary_component": 1})
		offer_details_list = []
		if len(self.offer_details) > 0:
			for row in self.offer_details:
				if row.offer_term not in offer_details_list:
					offer_details_list.append(row.offer_term)
				else :
					if row.offer_term == offer_term_with_monthly_salary_component:
						frappe.throw(_("Row #{0}: You cannot add {1} again.").format(row.idx,row.offer_term))

	def validate_value_in_offer_details(self):
		if len(self.offer_details) > 0:
			for row in self.offer_details:
				is_monthly_salary_component = frappe.db.get_value("Offer Term",row.offer_term,"custom_is_monthly_salary_component")
				if is_monthly_salary_component == 1:
					if not row.value:
						salary = frappe.db.get_value("MP Jobs Details ST",{"job_no":self.job_title},"salary")
						row.value = salary
						# frappe.throw(_("Row #{0}: Value cannot be 0").format(row.idx))

	def fetch_salary_tables_from_contract_type(self):
		if self.contract_type and self.is_new():
			self.earning = []
			self.deduction = []
			contract_type = frappe.get_doc("Contract Type ST", self.contract_type)
			if len(self.offer_details) > 0:
				if len(self.earning) == 0:
					for ear in contract_type.earning:
						earn = self.append("earning", {})
						earn.earning = ear.earning
						earn.abbr = ear.abbr
						# earn.percent = ear.percent
						earn.formula = ear.formula

				if len(self.deduction) == 0:
					for ded in contract_type.deduction:
						dedu = self.append("deduction", {})
						dedu.deduction = ded.deduction
						dedu.abbr = ded.abbr
						# dedu.percent = ded.percent
						dedu.formula = ded.formula
			else:
				frappe.throw(_("Please fill offer deatils first"))

	def calculate_salary_earnings_and_deduction(self):
		field_name_of_total_monthly_salary='total_monthly_salary'
		total_monthly_salary = 0
		salary_abbreviation_dict={}
		if len(self.offer_details) > 0:
			for offer in self.offer_details:
				monthly_salary_component = frappe.db.get_value('Offer Term', offer.offer_term, 'custom_is_monthly_salary_component')
				if monthly_salary_component == 1:
					total_monthly_salary = offer.value

		print(total_monthly_salary, '---total_monthly_salary')
		# total_monthly_salary = 0
		if total_monthly_salary > 0 :
			# logic for forumla having total_monthly_salary
			if len(self.earning)>0:
				for ear in self.earning:
					formula=ear.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)>-1:
						print(formula, '---formula---',total_monthly_salary, '---total_monthly_salary---')
						ear.amount = frappe.safe_eval(formula, None,{field_name_of_total_monthly_salary:total_monthly_salary})
						print(ear.amount, '--ear.amount')
						salary_abbreviation_dict[ear.abbr]=ear.amount
						
			if len(self.deduction)>0:
				for ded in self.deduction:
					formula=ded.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)>-1:
						ded.amount = frappe.safe_eval(formula, None,{field_name_of_total_monthly_salary:total_monthly_salary})
						salary_abbreviation_dict[ded.abbr]=ded.amount
						print(ded.amount, '--ear.amount')				
				
			# logic for forumla having abbr
			if len(self.earning)>0:
				for ear in self.earning:
					formula=ear.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)==-1:
						ear.amount = frappe.safe_eval(formula, None,salary_abbreviation_dict)
						print(ear.amount, '--ear.amount')
						
						
			if len(self.deduction)>0:
				for ded in self.deduction:
					formula=ded.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)==-1:
						ded.amount = frappe.safe_eval(formula, None,salary_abbreviation_dict)
						print(ded.amount, '--ear.amount')
								

	def validate_total_monthly_salary_earnings_and_deductions(self):
		# if not self.is_new():
		# monthly_salary = get_monthly_salary_from_job_offer(self.name)
		monthly_salary = 0
		if len(self.offer_details) > 0:
			for offer in self.offer_details:
				monthly_salary_component = frappe.db.get_value('Offer Term', offer.offer_term, 'custom_is_monthly_salary_component')
				if monthly_salary_component == 1:
					monthly_salary = offer.value

		if monthly_salary > 0 :
			total_monthly_salary = 0
			if len(self.earning)>0:
				for ear in self.earning:
					total_monthly_salary = total_monthly_salary + ear.amount

			# if len(self.deduction)>0:
			# 	for ded in self.deduction:
			# 		total_monthly_salary = total_monthly_salary + ded.amount

			if total_monthly_salary != monthly_salary:
				frappe.throw(_("Total of earnings amount must be {0} not {1}.").format(monthly_salary, total_monthly_salary))

	@frappe.whitelist()
	def get_salary_amount_from_man_power_planning(self):
		salary = 0
		if self.job_title:
			salary = frappe.db.get_value('MP Jobs Details ST', self.job_title , 'salary')
		print(salary, '----salary')
		return salary
	
	@frappe.whitelist()
	def get_salary_details_from_grade(self):

		print("get_salary_details_from_grade")

		if not self.grade:
			frappe.throw(_("Please Select Grade First."))

		self.earnings_details = []
		self.deduction_details = []

		if self.basic_salary_amount:
			grade_doc = frappe.get_doc("Employee Grade", self.grade)

			if self.basic_salary_amount > grade_doc.custom_max_basic_amount:
				frappe.throw(_("Basic Salary Amount Cann't be More Than {0} Grade Maximum Basic Amount.").format(grade_doc.custom_max_basic_amount))
			
			if self.basic_salary_amount < grade_doc.custom_minimum_basic_amount:
				frappe.throw(_("Basic Salary Amount Cann't be Less Than {0} Grade Manimum Basic Amount.").format(grade_doc.custom_minimum_basic_amount))

			basic = self.append("earnings_details", {})
			basic.earning = grade_doc.custom_basic_salary_component
			basic.amount = self.basic_salary_amount
			basic.maximum_amount = grade_doc.custom_max_basic_amount or 0
			basic.minimum_amount = grade_doc.custom_minimum_basic_amount or 0
			
			if len(grade_doc.custom_earnings) > 0:
				for ear in grade_doc.custom_earnings:
					earn = self.append("earnings_details", {})
					earn.earning = ear.earning
					earn.percentage = ear.percentage
					earn.maximum_amount = ear.maximum_amount or 0
					earn.minimum_amount = ear.minimum_amount or 0

					amount = (self.basic_salary_amount * ear.percentage) / 100

					if ear.maximum_amount and ear.maximum_amount < amount:
						earn.amount = ear.maximum_amount
						
					elif ear.minimum_amount and ear.minimum_amount > amount:
						earn.amount = ear.minimum_amount
						
					else:
						earn.amount = amount

			if len(grade_doc.custom_other_earnings) > 0:
				for other in grade_doc.custom_other_earnings:
					ot = self.append("earnings_details", {})
					ot.earning = other.earning
					ot.method = other.method

					if other.method == "Amount":
						ot.amount = other.amount

					if other.method == "Percentage":
						ot.percentage = other.percentage
						ot.maximum_amount = other.maximum_amount or 0
						ot.minimum_amount = other.minimum_amount or 0
						amount = (self.basic_salary_amount * other.percentage) / 100

						if other.maximum_amount and other.maximum_amount < amount:
							ot.amount = other.maximum_amount
							
						elif other.minimum_amount and other.minimum_amount > amount:
							ot.amount = other.minimum_amount
							
						else:
							ot.amount = amount

			if len(grade_doc.custom_deduction) > 0:
				for ded in grade_doc.custom_deduction:
					dedu = self.append("deduction_details", {})
					dedu.deduction = ded.deduction
					dedu.percentage = ded.percentage
					dedu.amount = (self.basic_salary_amount * dedu.percentage) / 100

	@frappe.whitelist()
	def fill_salary_tables(self):
		print("Inside Salary")
		# if self.contract_type and self.is_new():
		self.earning = []
		self.deduction = []
		contract_type = frappe.get_doc("Contract Type ST", self.contract_type)
		if len(self.offer_details) > 0:
			if len(self.earning) == 0:
				for ear in contract_type.earning:
					earn = self.append("earning", {})
					earn.earning = ear.earning
					earn.abbr = ear.abbr
					# earn.percent = ear.percent
					earn.formula = ear.formula

			if len(self.deduction) == 0:
				for ded in contract_type.deduction:
					dedu = self.append("deduction", {})
					dedu.deduction = ded.deduction
					dedu.abbr = ded.abbr
					# dedu.percent = ded.percent
					dedu.formula = ded.formula
		# else:
		# 	frappe.throw(_("Please fill offer deatils first"))
			
		field_name_of_total_monthly_salary='total_monthly_salary'
		total_monthly_salary = 0
		salary_abbreviation_dict={}
		if len(self.offer_details) > 0:
			for offer in self.offer_details:
				monthly_salary_component = frappe.db.get_value('Offer Term', offer.offer_term, 'custom_is_monthly_salary_component')
				if monthly_salary_component == 1:
					total_monthly_salary = offer.value

		print(total_monthly_salary, '---total_monthly_salary')
		# total_monthly_salary = 0
		if total_monthly_salary > 0 :
			# logic for forumla having total_monthly_salary
			
			set_formula_base_amount = True
			if len(self.earning)>0:
				for ear in self.earning:
					formula=ear.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)>-1:
						# print(formula, '---formula---',total_monthly_salary, '---total_monthly_salary---')
						ear.amount = frappe.safe_eval(formula, None,{field_name_of_total_monthly_salary:total_monthly_salary})
						salary_abbreviation_dict[ear.abbr]=ear.amount
						
						print(ear.amount, '--ear.amount')
						if ear.amount == 0 or ear.amount == None:
								set_formula_base_amount = False
						
			if len(self.deduction)>0:
				for ded in self.deduction:
					formula=ded.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)>-1:
						ded.amount = frappe.safe_eval(formula, None,{field_name_of_total_monthly_salary:total_monthly_salary})
						salary_abbreviation_dict[ded.abbr]=ded.amount
						
						print(ded.amount, '--ded.amount')
						if ded.amount == 0 or ded.amount == None:
							set_formula_base_amount = False					
				
			# logic for forumla having abbr
			if len(self.earning)>0:
				for ear in self.earning:
					formula=ear.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)==-1:
						ear.amount = frappe.safe_eval(formula, None,salary_abbreviation_dict)
						salary_abbreviation_dict[ear.abbr]=ear.amount
						
						print(ear.amount, '--ear.amount')
						if ear.amount == 0 or ear.amount == None:
								set_formula_base_amount = False
						
			if len(self.deduction)>0:
				for ded in self.deduction:
					formula=ded.formula
					if formula  and formula.find(field_name_of_total_monthly_salary)==-1:
						ded.amount = frappe.safe_eval(formula, None,salary_abbreviation_dict)
						salary_abbreviation_dict[ded.abbr]=ded.amount

						print(ded.amount, '--ded.amount')
						if ded.amount == 0 or ded.amount == None:
							set_formula_base_amount = False

			if set_formula_base_amount == True:
				frappe.msgprint(_("Amount is set in Tables"), alert=True)
			else:
				frappe.msgprint(_("Amoumt is not set"), alert=True)

	@frappe.whitelist()
	def fill_education_qualification_and_work_history(self):
		ja = frappe.get_doc("Job Application ST", self.job_application_reference)

		if len(ja.education) > 0 and len(self.education) < 1:
			for row in ja.education:
				educ = self.append("education", {})
				educ.school_univ = row.school_univ
				educ.qualification = row.qualification
				educ.custom_scientific_specification = row.custom_scientific_specification
				educ.level = row.level
				educ.year_of_passing = row.year_of_passing
				educ.class_per = row.class_per
				educ.maj_opt_subj = row.maj_opt_subj

		if len(ja.external_work_history) > 0 and len(self.external_work_history) < 1:
			for work in ja.external_work_history:
				history = self.append("external_work_history", {})
				history.company_name = work.company_name
				history.designation = work.designation
				history.salary = work.salary
				history.address = work.address
				history.contact = work.contact
				history.total_experience = work.total_experience

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	doc = frappe.get_doc("Job Offer ST", source_name)
	# doc.validate_employee_creation()

	def set_missing_values(source, target):
		target.custom_job_offer_reference = source.name
		target.personal_email = source.email
		target.status = "Active"
		target.first_name = source.candidate_name
		target.custom_employee_name_in_english = source.candidate_namein_english
		target.custom_country = source.country
		target.custom_there_is_a_security_survey = source.there_is_a_security_survey
		target.custom_religion = source.religion
		# target.custom_id__igama_no = source.id_igama_no
		target.department = source.main_department
		target.custom_hijri_birth_date = source.hijri_birth_date
		target.custom_section = source.section
		target.custom_sub_department = source.sub_department
		target.custom_contract_type = source.contract_type
		target.employment_type = source.employment_type
		target.custom_idresidency_number = source.id_igama_no
		target.custom_id_expiration_date = source.id_expiration_date
		target.cell_number = source.phone_no
		target.custom_building_number = source.building_number
		target.custom_neighbourhood = source.neighbourhood
		target.custom_postal_code = source.postal_code
		target.custom_street_name = source.street_name
		target.custom_city = source.city
		target.custom_additional_number = source.additional_number


	doc = get_mapped_doc(
		"Job Offer ST",
		source_name,
		{
			"Job Offer ST": {
				"doctype": "Employee",
				"field_map": {
					"first_name": "candidate_name",
					"employee_grade": "grade",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc