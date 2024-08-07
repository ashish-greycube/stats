# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet, get_root_of
from erpnext.utilities.transaction_base import delete_events


class JobFamilyST(NestedSet):
	nsm_parent_field = "parent_job_family_st"

	def autoname(self):
		root = get_root_of("Job Family ST")
		if root and self.job_family_st_name != root:
			self.name =self.job_family_st_name
		else:
			self.name = self.job_family_st_name

	def validate(self):
		if not self.parent_job_family_st:
			root = get_root_of("Job Family ST")
			if root:
				self.parent_job_family_st = root

	def on_update(self):
		if not (frappe.local.flags.ignore_update_nsm or frappe.flags.in_setup_wizard):
			super().on_update()

	def on_trash(self):
		super().on_trash()
		delete_events(self.doctype, self.name)


def on_doctype_update():
	frappe.db.add_index("Job Family ST", ["lft", "rgt"])


@frappe.whitelist()
def get_children(doctype, parent=None, job_family_st=None, is_root=False):
	if parent is None or parent == "All Job Families":
		parent = ""

	return frappe.db.sql(
		f"""
		select
			name as value,
			is_group as expandable
		from
			`tabJob Family ST` comp
		where
			ifnull(parent_job_family_st, "")={frappe.db.escape(parent)}
		""",
		as_dict=1,
	)


@frappe.whitelist()
def add_tree_node():
	from frappe.desk.treeview import make_tree_args

	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_job_family_st == "All Job Families" or not frappe.db.exists("Job Family ST", args.parent_job_family_st):
		args.parent_job_family_st = None
	frappe.get_doc(args).insert()