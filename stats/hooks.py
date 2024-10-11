app_name = "stats"
app_title = "Stats"
app_publisher = "GreyCube Technologies"
app_description = "Customization for stats"
app_email = "admin@greycube.in"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/stats/css/stats.css"
# app_include_js = "/assets/stats/js/stats.js"

# include js, css files in header of web template
# web_include_css = "/assets/stats/css/stats.css"
# web_include_js = "/assets/stats/js/stats.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "stats/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

doctype_js = {"ToDo" : "public/js/todo.js",
              "Employee":"public/js/employee.js",
              "Company":"public/js/company.js",
              "Department":"public/js/department.js",
              "Designation":"public/js/designation.js"
              }

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "stats/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "stats.utils.jinja_methods",
# 	"filters": "stats.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "stats.install.before_install"
# after_install = "stats.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "stats.uninstall.before_uninstall"
# after_uninstall = "stats.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "stats.utils.before_app_install"
# after_app_install = "stats.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "stats.utils.before_app_uninstall"
# after_app_uninstall = "stats.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "stats.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "ToDo": {
		"validate":["stats.api.set_todo_status_in_onboarding_procedures",
                    "stats.api.set_employee_company_email"]
	},
    "Employee": {
        "validate":"stats.api.calculate_years_of_experience"
	},
    "Leave Application": {
        "validate":"stats.api.check_leave_is_not_in_business_days"
	},
    "Offer Term": {
        "validate":"stats.api.check_monthly_salary_component_offer_term"
    },
    "Salary Structure": {
        "on_submit":"stats.api.create_salary_structure_assignment"
    },
    "Designation": {
        "validate":"stats.api.validate_weight_and_set_degree_based_on_weight"
    },
    "Attendance": {
        "validate":"stats.api.calculate_extra_working_hours"
    }    
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
        # at start of every year at 1:30 night
		"30 1 1 1 *": [
			"stats.api.set_no_of_business_trip_days_available_at_start_of_every_year",
		],
        "30 1 1 * *": [
            "stats.api.set_years_of_experience_at_start_of_every_month",
		],
        # at 11:30 PM every day
        "30 23 * * *": [
            "stats.api.set_scholarship_status_closed"
        ]
	},
    "daily": [
        "stats.api.create_employee_evaluation_yearly_and_half_yearly",
        "stats.api.create_employee_evaluation_based_on_employee_contract"
    ]
}
# 	"all": [
# 		"stats.tasks.all"
# 	],
# 	"daily": [
# 		"stats.tasks.daily"
# 	],
# 	"hourly": [
# 		"stats.tasks.hourly"
# 	],
# 	"weekly": [
# 		"stats.tasks.weekly"
# 	],
# 	"monthly": [
# 		"stats.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "stats.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "stats.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "stats.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["stats.utils.before_request"]
# after_request = ["stats.utils.after_request"]

# Job Events
# ----------
# before_job = ["stats.utils.before_job"]
# after_job = ["stats.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"stats.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

