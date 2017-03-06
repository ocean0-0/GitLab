
#!/usr/bin/python

import os
import sys
import re
import time
import ConfigParser

from datetime import datetime
from ftplib import FTP

ISOTIMEFORMAT='%Y_%m_%d_%X'

def upload_file(date, remote_path, local_path):

	cf = ConfigParser.ConfigParser()
	cf.read('base.conf')
	ftp_ip = cf.get('ftp', 'ftp_ip')
	ftp_port = cf.getint('ftp', 'ftp_port')
	ftp_user = cf.get('ftp', 'ftp_user')
	ftp_passwd=  cf.get('ftp', 'ftp_passwd')

	ftp = FTP()
	ftp_timeout = 30
	ftp_bufsize = 1024

	ftp.connect(ftp_ip, ftp_port, ftp_timeout)
	ftp.login(ftp_user, ftp_passwd)
	ftp.cwd('Desktop/web/static')

	try:
		ftp.cwd(date)
	except:
		ftp.mkd(date)
		ftp.cwd(date)

	f = open(local_path, 'rb')
	ftp.storbinary('STOR ' + remote_path, f, ftp_bufsize)
	f.close()
	ftp.quit()


def get_date():

	year = datetime.now().year
	month = datetime.now().month
	day = datetime.now().day

	date_value = str(year)
	if month <= 9:
		date_value += '0' + str(month)
	else:
		date_value += str(month)

	if day <= 9:
		date_value += '0' + str(day)
	else:
		date_value += str(day)

	return date_value


def main():

	cf = ConfigParser.ConfigParser()
	cf.read('base.conf')
	ipcam_ip =  cf.get('ipcam', 'ipcam_ip')

	while True:

		date = get_date()

		if os.path.exists('out.ogv'):
			file_name  =  time.strftime( ISOTIMEFORMAT, time.localtime()) + '.ogv'
			upload_file(date, file_name, 'out.ogv')
			os.system('rm -rf out.ogv')

		os.system('vlc rtsp://' + ipcam_ip + ':43794/profile1 &')
		time.sleep(10)
		os.system('recordmydesktop &' )
		time.sleep(5)
		os.system('killall recordmydesktop')
		os.system('kill -9 `pgrep vlc`')

		time.sleep(3600)


if __name__ == '__main__':

	main()


