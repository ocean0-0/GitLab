#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
sys.path.append('..')
from settings import render

class About:
    def GET(self):
        return render.about()
