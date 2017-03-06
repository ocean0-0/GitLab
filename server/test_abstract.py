#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.12.14
# Version : v1.2

import abc

class Test(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_testnames_timeout(self):
        return

    @abc.abstractmethod
    def get_testname(self, testname):
        return

    @abc.abstractmethod
    def get_timeout(self, testname, config_name):
        return

    @abc.abstractmethod
    def get_testcmd(self, testname):
        return
