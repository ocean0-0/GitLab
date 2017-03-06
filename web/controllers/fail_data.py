#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import sys
import json
sys.path.append('..')
from settings import render
from utility.scan import *
from utility.date import *

#get fail files in the specified folder
def get_fail_count_from_folder(name):
    count = 0
    dir = 'data/' + name
    if not os.path.exists(dir):
        return 0
    files = list_all_files(dir)
    if 0 == len(files):
        return -1
    for file in files:
        length = len('function_')
        if file[0:length] == 'function_' and file[length: length+4] == 'fail':
            count += 1
        length = len('system_')
        if file[0:length] == 'system_' and file[length: length+4] == 'fail':
            count += 1
    return count

class FailData:
    """get data for ajax in start.html"""
    def GET(self):
        num = []
        date = []
        year, month, day = get_year_month_day()
        for i in range(6):
            year, month, day = get_previous_day(year, month, day)
        for i in range(7):
            date.append(get_weekday_by_day(year, month, day))
            name =  generate_str_from_year_month_day(year, month, day)
            fail = get_fail_count_from_folder(name)
            num.append(fail)
            year, month, day = get_next_day(year, month, day)
        data = {'date':date, 'data':num}
        return json.dumps(data)
