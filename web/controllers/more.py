#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import sys
sys.path.append('..')
from settings import render
from utility.scan import *

class More:
    """list all files in the data folder
    """
    def GET(self):
        dirs = list_all_dirs('data/')
        if 0 == len(dirs):
            return render.error("没有测试数据！")

        '''sort dirs, then list them'''
        dirs.sort()
        dirs.reverse()
        return render.more(dirs)

