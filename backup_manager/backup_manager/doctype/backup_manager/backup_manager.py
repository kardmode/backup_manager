# -*- coding: utf-8 -*-
# Copyright (c) 2015, kardmode and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, split_emails, get_request_site_address, cstr, today,get_backups_path,get_datetime
from datetime import datetime, timedelta

import os
from frappe import _
#Global constants
verbose = 0
ignore_list = [".DS_Store"]

class BackupManager(Document):
	def take_backupsmethod(self):
		if cint(frappe.db.get_value("Backup Manager", None, "enable_backup")):
			take_backups()

def take_backups_hourly():
	take_backups_if("Hourly")

def take_backups_daily():
	take_backups_if("Daily")

def take_backups_weekly():
	take_backups_if("Weekly")

def take_backups_if(freq):
	if cint(frappe.db.get_value("Backup Manager", None, "enable_backup")):
		upload_frequency = frappe.db.get_value("Backup Manager", None, "upload_frequency")
		if upload_frequency == freq:
			take_backups()
		elif freq == "Hourly" and upload_frequency in ["Every 6 Hours","Every 12 Hours"]:
			last_backup_date = frappe.db.get_value('Backup Manager', None, 'last_backup_date')
			upload_interval = 12
			if upload_frequency == "Every 6 Hours":
				upload_interval = 6
			elif upload_frequency == "Every 12 Hours":
				upload_interval = 12
		
			if datetime.now() - get_datetime(last_backup_date) >= timedelta(hours = upload_interval):
				take_backups()
		

@frappe.whitelist()
def take_backups():
	frappe.db.begin()
	frappe.db.set_value('Backup Manager', 'Backup Manager', 'last_backup_date', datetime.now())
	frappe.db.commit()

	did_not_upload, error_log = [], []
	try:
		did_not_upload, error_log = backup_to_service()
		if did_not_upload: raise Exception
		#send_email(True, "Backup")
	except Exception:
		file_and_error = [" - ".join(f) for f in zip(did_not_upload, error_log)]
		error_message = ("\n".join(file_and_error) + "\n" + frappe.get_traceback())
		frappe.errprint(error_message)
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
	frappe.sendmail(recipients=recipients, subject=subject, message=message)


def backup_to_service():
	from frappe.utils.backups import new_backup
	from frappe.utils import get_files_path
	
	# upload files to files folder
	did_not_upload = []
	error_log = []
	
	if not frappe.db:
		frappe.connect()

	older_than = cint(frappe.db.get_value('Backup Manager', None, 'older_than'))
	if cint(frappe.db.get_value("Backup Manager", None, "enable_database")):
		# upload database
		backup = new_backup(ignore_files=True)
		# filename = os.path.join(get_backups_path(), os.path.basename(backup.backup_path_db))
		sync_folder(older_than,get_backups_path(), "database")

	BASE_DIR = os.path.join( get_backups_path(), '../file_backups' )

	if cint(frappe.db.get_value("Backup Manager", None, "enable_files")):
		Backup_DIR = os.path.join(BASE_DIR, "files")
		compress_files(get_files_path(), Backup_DIR)
		sync_folder(older_than,Backup_DIR, "files")

	
	if cint(frappe.db.get_value("Backup Manager", None, "enable_private_files")):
		Backup_DIR = os.path.join(BASE_DIR, "private/files")
		compress_files(get_files_path(is_private=1), Backup_DIR)
		sync_folder(older_than,Backup_DIR, "private/files")
		
	frappe.db.close()
	return did_not_upload, list(set(error_log))

def compress_files(file_DIR, Backup_DIR):
	if not os.path.exists(file_DIR):
		return
	
	from shutil import make_archive	
	archivename = datetime.today().strftime("%d%m%Y_%H%M%S")+'_files'
	archivepath = os.path.join(Backup_DIR,archivename)
	make_archive(archivepath,'zip',file_DIR)

	
def sync_folder(older_than,sourcepath, destfolder):
	destpath = "gdrive:" + destfolder
	
	delete_temp_backups(older_than,sourcepath)
	cmd_string = "rclone sync " + sourcepath + " " + destpath		
	err, out = frappe.utils.execute_in_shell(cmd_string)

def upload_file_to_service(older_than,filename, folder, compress):

	if not os.path.exists(filename):
			return
			
	if compress:
		from shutil import make_archive	
		BASE_DIR = os.path.join( get_backups_path(), '../file_backups' )
		Backup_DIR = os.path.join(BASE_DIR, folder)

		archivename = datetime.today().strftime("%d%m%Y_%H%M%S")+'_files'
		archivepath = os.path.join(Backup_DIR,archivename)
		
		delete_temp_backups(older_than,Backup_DIR)

		filename = make_archive(archivepath,'zip',filename)

	if os.path.exists(filename):	
		sourcepath = filename

		if os.path.isdir(filename):
			sourcepath = filename + "/"

		destpath = "gdrive:" + folder
		
		# cmd_string = "rclone --min-age 2d delete " + destpath		
		# err, out = frappe.utils.execute_in_shell(cmd_string)
		
		cmd_string = "rclone copy " + sourcepath + " " + destpath		
		err, out = frappe.utils.execute_in_shell(cmd_string)
		
		 
def delete_temp_backups(older_than, path):
	"""
		Cleans up the backup_link_path directory by deleting files older than 24 hours
	"""
	file_list = os.listdir(path)
	for this_file in file_list:
		this_file_path = os.path.join(path, this_file)
		if is_file_old(this_file_path, older_than):
			os.remove(this_file_path)

def is_file_old(db_file_name, older_than=24):
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
			if datetime.today() - file_datetime >= timedelta(hours = older_than):
				if verbose: print "File is old"
				return True
			else:
				if verbose: print "File is recent"
				return False
		else:
			if verbose: print "File does not exist"
			return True
			
if __name__=="__main__":
	backup_to_service()
		