import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_main_department(doctype, txt, searchfield, start, page_len, filters):
		
		department_list = frappe.get_all("Department", filters={"is_group":0}, fields=["parent_department"], as_list=1)
		unique = tuple(set(department_list))
		# print(unique, '----------ab')
		return unique