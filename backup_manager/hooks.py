# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "backup_manager"
app_title = "Backup Manager"
app_publisher = "kardmode"
app_description = "App for managing Backups"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "kardmode@gmail.com"
app_version = "0.0.1"
app_license = "GNU General Public License"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/backup_manager/css/backup_manager.css"
# app_include_js = "/assets/backup_manager/js/backup_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/backup_manager/css/backup_manager.css"
# web_include_js = "/assets/backup_manager/js/backup_manager.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "backup_manager.install.before_install"
# after_install = "backup_manager.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "backup_manager.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"backup_manager.tasks.all"
# 	],
 	"daily": [
		"backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backups_daily"
 	],
	"hourly": [
 		"backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backups_hourly"
	],
 	"weekly": [
 		"backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backups_weekly"
 	]
# 	"monthly": [
# 		"backup_manager.tasks.monthly"
# 	]
	# "daily_long": [
		# "backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backups_daily"
	# ],
	# "weekly_long": [
 		# "backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backups_weekly"
	# ]
}

# Testing
# -------

# before_tests = "backup_manager.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "backup_manager.event.get_events"
# }

