# -*- coding: utf-8 -*-
# Copyright (c) 2015, kardmode and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, split_emails, get_site_name,get_site_base_path, cstr, today,get_backups_path,get_datetime
from datetime import datetime, timedelta

import os
from frappe import _
#Global constants
verbose = 0
ignore_list = [".DS_Store"]

class BackupManager(Document):
	def onload(self):
		pass
		
	def validate(self):
		if self.send_notifications_on_error or send_notifications_on_success:
			if not self.send_notifications_to:
				frappe.throw(_("Please Enter An Email to Send Notifcations To"))


def take_backups_hourly():
	take_backups_if("Hourly")

def take_backups_daily():
	take_backups_if("Daily")

def take_backups_weekly():
	take_backups_if("Weekly")
	
def take_backups_monthly():
	take_backups_if("Monthly")

def take_backups_if(freq):
	if cint(frappe.db.get_value("Backup Manager", None, "enable_backup")):
		upload_frequency = frappe.db.get_value("Backup Manager", None, "upload_frequency")
		if upload_frequency == freq:
			take_backup()
		elif freq == "Hourly" and upload_frequency in ["Every 6 Hours","Every 12 Hours"]:
			last_backup_date = frappe.db.get_value('Backup Manager', None, 'last_backup_date')
			upload_interval = 12
			if upload_frequency == "Every 6 Hours":
				upload_interval = 6
			elif upload_frequency == "Every 12 Hours":
				upload_interval = 12
		
			if datetime.now() - get_datetime(last_backup_date) >= timedelta(hours = upload_interval):
				take_backup()
		

@frappe.whitelist()
def take_backup():
	# "Enqueue longjob for taking backup to dropbox"
	enqueue("backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backup_to_service", queue='long', timeout=1500)
	return
	
@frappe.whitelist()
def take_backup_to_service():
	
	did_not_upload, error_log = [], []
	try:
		did_not_upload, error_log = backup_to_service()
		if did_not_upload: raise Exception
		
		frappe.db.begin()
		frappe.db.set_value('Backup Manager', 'Backup Manager', 'last_backup_date', datetime.now())
		frappe.db.commit()
		
		if cint(frappe.db.get_value("Backup Manager", None, "send_notifications_on_success")):
			send_email(True, "Backup")
	except Exception:
		file_and_error = [" - ".join(f) for f in zip(did_not_upload, error_log)]
		error_message = ("\n".join(file_and_error) + "\n" + frappe.get_traceback())
		if cint(frappe.db.get_value("Backup Manager", None, "send_notifications_on_error")):
			send_email(False, "Backup", error_message)
		

		
	

def send_email(success, service_name, error_status=None):
	if success:
		subject = "Backup Upload Successful"
		message ="""<h3>Backup Uploaded Successfully</h3><p>Hi there, this is just to inform you
		that your backup was successfully uploaded to your %s account.</p>
		""" % service_name

	else:
		subject = "[Warning] Backup Upload Failed"
		message ="""<h3>Backup Upload Failed</h3><p>Oops, your automated backup to %s
		failed.</p>
		<p>Error message: %s</p>
		<p>Please contact your system manager for more information.</p>
		""" % (service_name, error_status)

	if not frappe.db:
		frappe.connect()
		

	recipients = split_emails(frappe.db.get_value("Backup Manager", None, "send_notifications_to"))
	
	if recipients:
		frappe.sendmail(recipients=recipients, subject=subject, message=message)


def backup_to_service():
	from frappe.utils.backups import new_backup
	from frappe.utils import get_files_path
	
	# upload files to files folder
	did_not_upload = []
	error_log = []
	
	
	domain_settings = frappe.get_single("Backup Manager")
	older_than_hrs = cint(domain_settings.older_than)
	cloud_sync = cint(domain_settings.cloud_sync)
	enable_database = cint(domain_settings.enable_database)
	enable_files = cint(domain_settings.enable_files)
	enable_private_files = cint(domain_settings.enable_private_files)
	site = get_site_base_path()[2:]
	BASE_DIR = os.path.join( get_backups_path(), '../file_backups' )
	public_files_backup_DIR = os.path.join(BASE_DIR, "files")
	private_files_backup_DIR = os.path.join(BASE_DIR, "private/files")

	if enable_database:
		backup = new_backup(older_than_hrs,ignore_files=True)
		if cloud_sync:
			sync_folder(site,older_than_hrs,get_backups_path(), "database",did_not_upload,error_log)


	if enable_files:
		compress_files(get_files_path(), public_files_backup_DIR)
		delete_temp_backups(older_than_hrs,public_files_backup_DIR)
		if cloud_sync:
			sync_folder(site,older_than_hrs,public_files_backup_DIR, "public-files",did_not_upload,error_log)

	
	if enable_private_files:
		compress_files(get_files_path(is_private=1), private_files_backup_DIR,"private")
		delete_temp_backups(older_than_hrs,private_files_backup_DIR)
		if cloud_sync:
			sync_folder(site,older_than_hrs,private_files_backup_DIR, "private-files",did_not_upload,error_log)
		
	

	return did_not_upload, list(set(error_log))

def compress_files(file_DIR, Backup_DIR,prefix=None):
	if not os.path.exists(file_DIR):
		return
	
	from shutil import make_archive	
	
	if prefix and prefix != " ":
		archivename = datetime.today().strftime("%d%m%Y_%H%M%S")+'_'+str(prefix)+'_files'
	else:
		archivename = datetime.today().strftime("%d%m%Y_%H%M%S")+'_files'
	archivepath = os.path.join(Backup_DIR,archivename)
	make_archive(archivepath,'tar',file_DIR)

	
def sync_folder(site,older_than_hrs,sourcepath, destfolder,did_not_upload,error_log):
	# destpath = "gdrive:" + destfolder + " --drive-use-trash"
	final_dest = str(site) + "/" + destfolder
	final_dest = final_dest.replace(" ", "_")
	destpath = "gdrive:"+ final_dest

	cmd_string = "rclone sync " + sourcepath + " " + destpath
	
	try:
		err, out = frappe.utils.execute_in_shell(cmd_string)
		if err: raise Exception
	except Exception:
		did_not_upload  = True
		error_log.append(Exception)

		
		 
def delete_temp_backups(older_than_hrs, path):

	"""
		Cleans up the backup_link_path directory by deleting files older than x hours
	"""
	file_list = os.listdir(path)
	for this_file in file_list:
		this_file_path = os.path.join(path, this_file)
		if is_file_old(this_file_path, older_than_hrs):
			os.remove(this_file_path)
			
			

def is_file_old(db_file_name, older_than_hrs=24):
		"""
			Checks if file exists and is older than specified hours
			Returns ->
			True: file does not exist or file is old
			False: file is new
		"""
		if os.path.isfile(db_file_name):
			from datetime import timedelta
			#Get timestamp of the file
			file_datetime = datetime.fromtimestamp\
						(os.stat(db_file_name).st_ctime)
			if datetime.today() - file_datetime >= timedelta(hours = older_than_hrs):
				if verbose: print("File is old")
				return True
			else:
				if verbose: print("File is recent")
				return False
		else:
			if verbose: print("File does not exist")
			return True

			
if __name__=="__main__":
	backup_to_service()
		