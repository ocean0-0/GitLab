#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import sys
sys.path.append('..')
from settings import render
from utility.scan import *

file_type = ['function_','system_','pressure_','performance_','compile_','firmware_','selenium_','api_']
def check_file_type(filename):
    for f in file_type:
        if re.match(f,filename) != None:
            return 0
        elif f == file_type[-1]:
            return -1

class Folder:
    def GET(self, dirname):
        if not os.path.exists('data/' + str(dirname)):
            return render.error('没有测试数据！')
        files = list_all_files('data/' + str(dirname))
        if 0 == len(files):
            return render.error("None")
        for f in files:
            if check_file_type(f) == -1:
                return render.error(file + ' error!')
        static_files = list_all_files('static/' + str(dirname))
        return render.folder(dirname, files, static_files)
