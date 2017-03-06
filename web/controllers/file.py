#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
sys.path.append('..')
from settings import render

class ShowFileContent:
    """show all content in the specified file
    """
    def GET(self, id1, id2):
        dir = 'data/' + str(id1)
        if not os.path.exists(dir):
            return render.error("亲，还没有测试哎！")
        name = 'data/' + str(id1) + '/' + str(id2)
        if not os.path.isfile(name):
            return render.error("亲，没有测试结果给你看哦！")
        '''open file, then convert it to html format '''
        file = open(name, 'r')
        buf = ''
        lines = file.readlines()
        for i in range(len(lines)):
            if 1 == len(lines[i]) and lines[i][0] == '\n':
                buf += '<br/>'
            else:
                buf += '<p>' + str(i) + ':' +  lines[i] +'</p>'
        file.close()
        return render.file(buf)

