# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

 import frappe
from frappe.utils.nestedset import NestedSet


class JobFamilyST(NestedSet):
	nsm_parent_field = "parent_job_family"
	#pass
