frappe.ui.form.on("Job Family ST", {
	onload: function (frm) {
		frm.set_query("parent_job_family_st", function () {
			return { filters: [["Job Family ST", "is_group", "=", 1]] };
		});
	},
	refresh: function (frm) {
		// read-only for root department
		if (!frm.doc.parent_job_family_st && !frm.is_new()) {
			frm.set_read_only();
			frm.set_intro(__("This is a root job family and cannot be edited."));
		}
	},
	validate: function (frm) {
		if (frm.doc.name == "All Job Families") {
			frappe.throw(__("You cannot edit main root node."));
		}
	},
});
