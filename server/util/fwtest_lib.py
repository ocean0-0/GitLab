# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.09.29

###############
# FW test API #
###############

import board_lib
import db,time
import util

def get_board_info(ip, *argv):
    status = {}
    status_param = ('sdkVersion', 'macAddr', 'protocol', 'encryption', 'bssid',
            'state', 'dns1', 'buildTime', 'ipAddr', 'upTime', 'fwVersion',
            'subnetMask', 'gateway', 'uuid')
    if len(argv) != 0:
        for t in argv:
            if t not in status_param:
                return 112
    re = board_lib.check_board_on_line(ip)
    if re == 0:
        re = board_lib.get_board_info(ip)
        if re != -1:
            if len(argv) == 0:
                return re['data']
            else:
                for t in argv:
                    status[t] = re['data'][t]
                return status
    return 112

def set_fwtest_status(db_name, table_name, identity, value):
    db.update(db_name, table_name, identity, status = value)

def get_fwtest_status(db_name, table_name, identity, value):
    status = db.find(db_name, table_name, identity, value)[value]
    return status

def check_fw_board_online(ip):
    return board_lib.check_board_on_line(ip)

def list_online_board(ip_start, ip_end):
    ip_list = []
    ip = ip_start
    ip_start_list = ip_start.split('.')
    ip_end_list = ip_end.split('.')
    for i in range(3):
        if ip_start_list[i] != ip_end_list[i]:
            return -1
    if int(ip_start_list[3]) > int(ip_end_list[3]):
        ip = ip_end
        ip_tmp = ip_start_list
        ip_start_list = ip_end_list
        ip_end_list = ip_tmp

    while True:
        print ip
        if board_lib.check_board_on_line(ip) == 0:
            ip_list.append(ip)
        if int(ip_start_list[3]) == int(ip_end_list[3]):
            break
        ip_start_list[3] = str(int(ip_start_list[3]) + 1)
        ip = ''
        for i in range(4):
            ip += (ip_start_list[i] + '.')
        ip = ip[:-1]
    return ip_list

def check_board_status(db_name, table_name, ip):
    for i in db.get_allid(db_name, table_name):
        if db.find(db_name, table_name, i, 'ip')['ip'] == ip:
            return db.find(db_name, table_name, i, 'status')['status']
    return None

def get_ip_from_sensor(db_name, table_name, sensor):
    for i in db.get_allid(db_name, table_name):
        if db.find(db_name, table_name, i, 'sensor')['sensor'] == sensor:
            return db.find(db_name, table_name, i, 'ip')['ip']
    return None

def get_table_ip_sensor(config_name, proj_name):
    return util.get_dict_from_config(config_name, proj_name)

if __name__ == '__main__':
    #print list_online_board('10.0.10.10','10.0.10.27')
    print check_board_status('../ipcamtest.db', 'board', '10.0.10.27')
    print get_table_ip_sensor('../config_server.ini', 'table_fwtest')
