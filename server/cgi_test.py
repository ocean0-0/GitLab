#!/usr/bin/python
#-*- coding: UTF-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.12.08
# Version : v1.1

import os
import re
import sys
import time
import threading
import update_kernel
from util import util
from datetime import datetime
from util.board_lib import *
from util.common_lib import *
from cgi_test import cgi_main

log_dir = 'log_dir'
usr_board = 'admin'
psd_board = '123456'
config_name = 'config_server.ini'
config_cgi = os.getcwd() + '/cgi_test/config.ini'

def send_file(config_name, local_log, remote_log):
    info = util.get_dict_from_config(config_name, 'ftp_server')
    ip = info['ip']
    usr = info['usr']
    psd = info['psd']
    dirname = info['dirname']
    print 'send pass'
    #util.send_file_to_webserver(ip, usr, psd, dirname, local_log, remote_log)

def handle_systest(config_name, client_ip, log_dir):
    cgi = cgi_main.CGI()
    hex_ip = util.get_ip_hex_format(client_ip)
    remote_pass_log_pre = '/system_pass_'+hex_ip + '_'
    remote_fail_log_pre = '/system_fail_'+hex_ip + '_'
    cgi_test_info = util.get_dict_from_config(config_name,'systemtest')
    for test_name in cgi_test_info['system']:
        print test_name
        log_name = log_dir + '/' + client_ip + test_name + '.log'
        time_start = 'start time: ' + str(util.get_current_time()) + '\n'
        with open(log_name, 'w') as f:
            f.write(time_start)
        cgi.set_ip(client_ip)
        cgi.set_usr(usr_board)
        cgi.set_psd(psd_board)
        cgi.set_testname(test_name)
        cgi.set_logname(log_name)
        cgi.set_config_name(config_cgi)
        cgi.cgi_main()
        time_end = 'end time: ' + str(util.get_current_time()) + '\n'
        with open(log_name, 'a+') as f:
            f.write(time_end)
        f = open(log_name,'r')
        pos = 0
        for line in range(10):
            while True:
                pos = pos - 1
                try:
                    f.seek(pos, os.SEEK_END)
                    if f.read(1) == '\n':
                        break
                except:
                    f.seek(0,0)
            line = f.readline().strip()
            if (len(re.findall('timeout',line)) != 0) or (len(re.findall('failed',line)) != 0) \
                    or (len(re.findall('error',line)) != 0):
                remote_log = remote_fail_log_pre + test_name +'.log'
                print 'fail'
                send_file(config_name, log_name, remote_log)
                break
            elif len(re.findall('succeed',line)) != 0:
                remote_log = remote_pass_log_pre + test_name +'.log'
                print 'success'
                send_file(config_name, log_name,remote_log)
                break
        f.close()

def start_cgi_test():
    ip_list = get_routine_test_ip_list(config_name, 'client info').split(',')
    while True:
        time.sleep(10)
        if datetime.now().hour == 15 and datetime.now().minute == 10:
            print '='*10
            ip_l = []
            for i in ip_list:
                if check_board_on_line(i) == 0:
                    ip_l.append(i)
            for ip_client in ip_l:
                if check_board_on_line(ip_client) == 0:
                    print ip_client
                    handle_systest(config_name, ip_client, log_dir)
                    time.sleep(2)

def update_image():
    ip_list = get_routine_test_ip_list(config_name, 'client info').split(',')
    while True:
        time.sleep(10)
        if datetime.now().hour == 14 and datetime.now().minute == 35:
            print '='*10
            ip_l = []
            for i in ip_list:
                if check_board_on_line(i) == 0:
                    ip_l.append(i)
            update_kernel.start_update(config_name, True, *ip_l)

if __name__ == '__main__':
    t_update = threading.Thread(target = update_image)
    t_update.start()
    t_systest = threading.Thread(target = start_cgi_test)
    t_systest.start()
