
#!/usr/bin/python

import os
import sys
import re

def list_all_files(root_dir):
	filename = []
	for dirpath, dirnames, filenames in os.walk(root_dir):
    		for file in filenames:
			filename.append(file)

	return  filename

def list_all_dirs(root_dir):
	dirname = []
	for dirpath, dirnames, filenames in os.walk(root_dir):
		for dir in dirnames:
			dirname.append(dir)
	return dirname


