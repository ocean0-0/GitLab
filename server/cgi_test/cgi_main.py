# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 28/10/16
# Version : 1.0

# This module helps us to test IP Camera cgi.
#
# It get necessary paramenters via set-function.
#
# This module prodives eleven functions and an execption:
# set_ip() -- Set ip which IPCamera  you want to test.
# get_ip() -- Get ip(default or you set).
# set_usr() -- Set username,when you enter url in browser
#              you need verify user name and password.
# get_usr() -- Get user name.
# set_psd() -- See set_usr().
# get_psd() -- Get password.
# set_testname() -- Set cgi name.
# get_testname() -- Get cgi name.
# set_config_name() -- Set the configruation file path, the config contains cgi url,test command.
# get_config_name() -- Get configruation file path.
# cgi_main() -- main function

from ipcam_class import IPCTest

class GetcgiError(Exception):
    opt = ''
    msg = ''
    def __init__(self, msg, opt = ''):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    def __str__(self):
        return self.msg


class CGI(object):

    ip = ''
    usr = 'admin'
    psd = '123456'
    test_name = ''
    log_name = ''
    config_name = 'config.ini'

    def __init__(self):
        pass

    def set_ip(self, ip):
        self.ip = ip

    def get_ip(self):
        return self.ip

    def set_usr(self, usr):
        self.usr = usr

    def get_usr(self):
        return self.usr

    def set_psd(self, psd):
        self.psd = psd

    def get_psd(self):
        return self.psd

    def set_testname(self, test_name):
        self.test_name = test_name

    def get_testname(self):
        return self.test_name

    def set_logname(self, log_name):
        self.log_name = log_name

    def get_logname(self):
        return self.log_name

    def set_config_name(self, config_name):
        self.config_name = config_name

    def get_config_name(self):
        return self.config_name

    def cgi_main(self):
        if self.ip == '' or self.test_name == '':
            raise GetcgiError('invalid argument: ip or test_name is NULL', 'pass parameters')
        else:
            ipcam = IPCTest(self.ip, self.usr, self.psd, self.log_name, self.config_name)
            ipcam.main(self.test_name)

if __name__ == '__main__':
    test = CGI()
    test.set_ip('10.0.2.97')
    test.set_usr('admin')
    test.set_psd('123456')
    test.set_testname('reboot')
    test.set_logname('test.log')
    #test.set_testname('audio')
    test.set_config_name('config.ini')
    test.cgi_main()
