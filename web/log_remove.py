#!/usr/bin/python

'''
uage:
	python log_remove.py [path1] [path2] ...
'''

import os
import sys
import re
import time
import signal
import subprocess


'''
global path is set initially
'''
path = []
g_exit = 0


'''
signal process, main thread can catch signal
'''
def sig_process(sig, frame):
	global g_exit
	g_exit = 1
	print 'catch signal here'


'''
get all folders name below specified delete path
'''
def get_all_folders(del_path):
	dirs = os.listdir(del_path)
	idx = 0
	while idx < len(dirs):

		'''
		only search folder
		'''
		if True !=  os.path.isdir(del_path + '/' + dirs[idx]):
			del dirs[idx]
			continue

		'''
		only search digital folder
		'''
		if 0 != len(re.findall(r'[^\d]', dirs[idx])):
			del dirs[idx]
			continue

		idx += 1


	return dirs


'''
delete folder name
'''
def del_folder_file(del_path, date):
	global g_exit

	'''
	check if path exits definitely
	'''
	if True != os.path.exists(del_path):
		print 'path does not exist'
		return

	dirs = get_all_folders(del_path)

	'''
	begin to delete files here
	'''
	for idx in range(len(dirs)):
		if date > int(dirs[idx]):

			full_path = del_path + '/' + dirs[idx]
			print 'delete folder ' + full_path
			subprocess.call('rm -rf ' + full_path, shell=True)

			'''
			got exit while delete file
			'''
			if g_exit:
				os._exit(0)

'''
function entry
'''
def main():
	global path
	global g_exit

	'''
	check param number
	'''
	if len(sys.argv) <= 1:
		print 'no folder path can be found'
		return

	'''
	add folder from command input line, get param form second input
	'''
	for idx in range(len(sys.argv) -1):
		path.append(sys.argv[idx +1])

	signal.signal(signal.SIGINT,  sig_process)	
	signal.signal(signal.SIGTERM, sig_process)	

	while True:
		day = time.localtime()
		date = '%d%02d01' % (day.tm_year, day.tm_mon)
	
		for i in range(len(path)):
			del_folder_file(path[i], int(date))

		'''
		begin to sleep one month
		'''
		print 'now sleep for 30 days'
		time.sleep(30 * 24 * 3600)

		if g_exit:
			os._exit(0)	

'''
test entry
'''
if __name__ == '__main__':
	main()


