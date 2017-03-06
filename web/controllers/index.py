#!/usr/bin/env python
#-*-coding: utf-8 -*-
import sys
sys.path.append('..')
from settings import render
from utility.date import *

class Index:
    def GET(self):
        year, month, day = get_year_month_day()
        name = generate_str_from_year_month_day(year, month, day)
        return render.start(name)


