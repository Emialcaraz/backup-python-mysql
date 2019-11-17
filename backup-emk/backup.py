#!/usr/bin/python
 
###########################################################
#
# This python script is used for mysql database backup
# using mysqldump and tar utility.
#
# Written by : Emiliano Alcaraz

#
# Created date: June 26, 2019
# Tested with : Python 2.7 
# Script Revision: 1.0
#
##########################################################
 
# Import required python libraries
 
import os
import time
import datetime
import pipes
import humanize

########################################################## e-mail

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


server = 'mail.example.es'
user = 'backup@example.es'
password = 'passwordemail'

recipients = 'youremail@hotmail.com'
sender = 'backup@example.es'

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Link"
msg['From'] = user
msg['To'] = recipients

DBLIST = []
########################################################## no e-mail

# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup.
# To take multiple databases backup, create any file like /backup/dbnames.txt and put databases names one on each line and assigned to DB_NAME variable.
 
DB_HOST = 'localhost'  
DB_USER = 'root' 
DB_USER_PASSWORD = 'DB_USER_PASSWORD'
DB_NAME = '/backup-emk/dbnameslist.txt' # directory of db file with databases name to read
BACKUP_PATH = '/backup-emk/db-backup' # Directory of the backup path
 
# Getting current DateTime to create the separate backup folder like "2019-11-22".
DATETIME = time.strftime('%Y-%m-%d')
TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME
 
# Create target directory & all intermediate directories if don't exists
if not os.path.exists(TODAYBACKUPPATH):
    os.makedirs(TODAYBACKUPPATH) 
    print("Directory " , TODAYBACKUPPATH ,  " Created ")
else:    
    print("Directory " , TODAYBACKUPPATH ,  " already exists")

 
# Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
print ("checking for databases names file.")
if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = 1
    print ("Databases file found...")
    print ("Starting backup of all dbs listed in file " + DB_NAME)
else:
    print ("Databases file not found...")
    print ("Starting backup of database " + DB_NAME)
    multi = 0

# Starting actual database backup process.
if multi:
   in_file = open(DB_NAME,"r")
   flength = len(in_file.readlines())
   in_file.close()
   p = 1
   dbfile = open(DB_NAME,"r")
 
   while p <= flength:
       db = dbfile.readline()   # reading database name from file
       db = db[:-1]         # deletes extra line
       dumpcmd = "mysqldump --user=" + DB_USER + " --password=" + pipes.quote(DB_USER_PASSWORD) + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
       print(dumpcmd)
       os.system(dumpcmd)
       gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
       os.system(gzipcmd)
       DBLIST.append(db)
       p = p + 1
   dbfile.close()
else:
   db = DB_NAME
   dumpcmd = "mysqldump --user=" + DB_USER + " --password=" + pipes.quote(DB_USER_PASSWORD) + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
   os.system(dumpcmd)
   gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
   os.system(gzipcmd)
 
print ("")
print ("Backup script completed")
print ("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")

########################################################## e-mail

# Create the body of the message (a plain-text and an HTML version).
text = "Backup system - please see the e-mail with another device "
html = """<html>
<head>
<style>
body {
  color: black;
}

h1 {
  color: green;
}
#customers {
  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

#customers td, #customers th {
  border: 1px solid #ddd;
  padding: 8px;
}

#customers tr:nth-child(even){background-color: #f2f2f2;}

#customers tr:hover {background-color: #ddd;}

#customers th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #4CAF50;
  color: white;
}
</style>
</head>
<body>

<h1>Databases backup system</h1>
<p>The backup system are already executed. Please don't reply this e-mail.
This system has been designed for *example* website. DATA5</p>

<table id="customers">
  <tr>
    <th>Databases </th>
    <th>Datetime</th>
    <th>Size</th>
    <th>All Sizes</th>
  </tr>
  <tr>
    <td>DATA1</td>
    <td>DATA2</td>
    <td>DATA3</td>
    <td>DATA4</td>
  </tr>
</table>

<p>The database backup system it was developed by Emiliano Alcaraz.</p>

</body>
</html>
"""

########################################################## get size of directory function 
def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

########################################################## tricky way to add things to text 
html = html.replace("DATA1", str(DBLIST).strip('[]'))  # databases list
html = html.replace("DATA2", DATETIME) # datetime
html = html.replace("DATA3", humanize.naturalsize(get_size('/home/backup-emk/db-backup/' + DATETIME)))
html = html.replace("DATA4", humanize.naturalsize(get_size('/home/backup-emk/db-backup/')))
html = html.replace("DATA5", "Your backups have been created in '" + TODAYBACKUPPATH + "' directory") 

########################################################## tricky way to add things to text 

# here we delete the oldest directory and files.
dirlist = []

for i,j,y in os.walk('/home/backup-emk/db-backup/'):
    dirlist.append(i)

dirlist.pop(0)  # we pop 0, because the 0 is /home/backup-emk/db-backup with no directory.

if len(dirlist) >= 5: # Only five days to backup, we can change this to another number.
    oldest_subdir = min(dirlist, key=os.path.getmtime)
    print(oldest_subdir)
    filesdir = os.listdir(oldest_subdir)
    print("removiendo archivos")
    for x in filesdir:
      os.remove(oldest_subdir + '/' + x)
      print(x)
    os.rmdir(oldest_subdir)
    print("se removio el directorio")
    print(oldest_subdir)


# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.

msg.attach(part1)
msg.attach(part2)

# Send the message via local SMTP server.

s = smtplib.SMTP_SSL(server,465) 
s.ehlo()
s.login(user, password)
s.sendmail(user, recipients, msg.as_string())
s.sendmail(user, 'support@example.com', msg.as_string())
s.quit()

########################################################## finish mysql backup system
