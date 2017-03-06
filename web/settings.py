#!/usr/bin/env python
#-*- coding: utf-8 -*-

import web

#设置模板目录和模板缓存
render = web.template.render('templates/', base='base', cache=False)

#在模板中可以使用 static 该全局对象
web.template.Template.globals['static'] = '/static'
