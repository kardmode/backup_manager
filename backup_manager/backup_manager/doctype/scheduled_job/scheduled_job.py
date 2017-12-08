# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, getdate,date_diff,get_datetime
from frappe.model.document import Document

class ScheduledJob(Document):
	def run_all_jobs(self,freq):
		if freq == "hourly":
			run_jobs_hourly()
		elif freq == "daily":
			run_jobs_daily()
		elif freq == "weekly":
			run_jobs_weekly()
		elif freq == "monthly":
			run_jobs_monthly()

def run_jobs_hourly():
	pass

def run_jobs_daily():
	pass

def run_jobs_weekly():
	deactivate_relieved_employees()

def run_jobs_monthly():
	deactivate_relieved_employees()


def deactivate_relieved_employees():
	employees = frappe.db.sql("""select name,employee_name,relieving_date from `tabEmployee` where relieving_date IS NOT NULL and status <> %(status)s""", {"status": "Left"}, as_dict=1)	

	
	
	for emp in employees:
		frappe.errprint(emp)
		
		from datetime import datetime
		currentDay = datetime.now().day
		currentMonth = datetime.now().month
		currentYear = datetime.now().year
		
		
		relieving_date = get_datetime(emp.relieving_date)
		relieving_day = relieving_date.day
		relieving_month = relieving_date.month
		relieving_year = relieving_date.year
		
		# frappe.errprint(relieving_date)
		# frappe.errprint(relieving_day)
		# frappe.errprint(relieving_month)
		# frappe.errprint(relieving_year)
		
		# frappe.errprint(currentDay)
		# frappe.errprint(currentMonth)
		# frappe.errprint(currentYear)
		
		if relieving_year < currentYear:
			frappe.errprint("change to left - year different")

			frappe.db.begin()
			frappe.db.set_value('Employee', emp.name, 'status', 'Left')
			frappe.db.commit()
				
		elif relieving_year == currentYear:
			if relieving_month < currentMonth:
				frappe.errprint("change to left - year same")
				frappe.db.begin()
				frappe.db.set_value('Employee', emp.name, 'status', 'Left')
				frappe.db.commit()
			else:
				frappe.errprint("no change-relieving month same or greater")
		
	
	
	