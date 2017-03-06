# -*- coding:utf-8 -*-
#!/usr/bin/python

import os
import sys
import re
import time
from datetime import datetime


def get_current_time():
	
	"""
		get system time
		time format: 2016-09-28 10:36
	"""
	TIMEFORMAT = '%Y-%m-%d--%H:%M:%S'

	return time.strftime(TIMEFORMAT)

# check days for each month
def get_month_days(year, month):

	assert(year > 0 and year <= 9999)
	assert(month > 0 and month <= 12)

	if month == 1:
		return 31
	elif month == 2:
		if year % 400 == 0:
			return 29
		elif year % 100 != 0 and year % 4 == 0:
			return 29
		else:
			return 28
	elif month == 3:
		return 31
	elif month == 4:
		return 30
	elif month == 5:
		return 31
	elif month == 6:
		return 30
	elif month == 7:
		return 31
	elif month == 8:
		return 31
	elif month == 9:
		return 30
	elif month == 10:
		return 31
	elif month == 11:
		return 30
	else:
		return 31


def get_previous_day(year, month, day):

	assert(year > 0 and year <= 9999);
	assert(month >= 1 and month <= 12)
	assert(day >= 1 and day <= 31)

	if day > 1:
		return year, month, day-1

	elif month > 1:
		return year, month -1, get_month_days(year, month -1)

	else:
		return year-1, 12, 31


def get_next_day(year, month, day):

	assert(year > 0 and year <= 9999);
	assert(month >= 1 and month <= 12)
	assert(day >= 1 and day <= 31)

	if day == 31:
		if month == 12:
			return year+1, 1, 1
		else :
			return year, month +1, 1
		
	elif day == 30:
		if month == 4 or month == 6 or month == 9 or month == 11:
			return year, month +1, 1
		else:
			return year, month, day +1  

	elif day == 29:
		if 29 == get_month_days(year, month):
			return year, month +1, 1
		else:
			return year, month, day +1

	elif day == 28:
		if 28 == get_month_days(year, month):
			return year, month +1, 1
		else:
			return year, month, day +1
	else:
		return year, month, day +1


def get_weekday():
	
	day = time.localtime()
	weekday = time.strftime("%A", day)

	if weekday == 'Monday':
		return 1
	elif weekday == 'Tuesday':
		return 2
	elif weekday == 'Wednesday':
		return 3
	elif weekday == 'Thursday':
		return 4
	elif weekday == 'Friday':
		return 5
	elif weekday == 'Saturday':
		return 6
	else:
		return 7


def get_weekday_by_day(year, month, day):

	date = {'1':'周一', '2':'周二', '3':'周三', '4':'周四', '5':'周五', '6':'周六', '0':'周日'}
	anyday=datetime(year, month, day).strftime("%w")
	return date[anyday]


def get_year_month_day():

	year = datetime.now().year
	month = datetime.now().month
	day = datetime.now().day

	return year, month, day


def generate_str_from_year_month_day(year, month, day):

	if month < 10:

		if day < 10:
			name = str(year) + '0' + str(month) + '0' + str(day)
		else:
			name = str(year) + '0' + str(month) + str(day)
	else:
		if day < 10 :
			name = str(year) + str(month) + '0' + str(day)
		else:
			name = str(year) + str(month) + str(day)

	return name


 

