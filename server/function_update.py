#!/usr/bin/python
#-*- coding: UTF-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2017.01.16
# Version : v1.3

import time
from datetime import datetime
import update_kernel
from util.board_lib import *
from util.common_lib import *
from util.fwtest_lib import *

config_name = 'config_server.ini'

def update():
    """The function is used to regularly update board's kernel
       and board's ips will be picked up from config_server.ini.
    """
    ip = get_routine_test_ip_list(config_name, 'client info')
    ip_list = ip.split(',')
    time_update_kernel = get_update_kernel_time(config_name, 'update_kernel')
    while True:
        time.sleep(10)
        if datetime.now().hour == int(time_update_kernel[0]) and datetime.now().minute == int(time_update_kernel[1]):
            function_status = {}
            print 'update kernel:',ip_list
            update_kernel.start_update(config_name, False, *ip_list)
            time.sleep(55)

if __name__ == '__main__':
    update()
