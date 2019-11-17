## This python script is used for MYSQL DB backup

using mysqldump and tar utility.
Written by : Emiliano Alcaraz

Created date: June 26, 2019
Tested with : Python 2.7 
Script Revision: 1.0

# Requirements: 
* datetime
* pipes
* humanize 
* smtplib


# Features
* you can receive emails with the information of the backup.
* Add your database and email credentials.

# Crontab
* You can run the script in crontab to run the backup daily.

![alt text](https://i.gyazo.com/101ead5337dc55a65b09ea7554921615.png)
