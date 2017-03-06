#!/usr/bin/python
#-*- coding: UTF-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.12.09
# Version : v1.2


from datetime import datetime
from util import util
from util import common_lib
import test_abstract
import global_var

config_name = 'config_server.ini'
log_dir = 'log_dir'

def check(ip_client):
    re = util.get_dict_from_config(config_name, 'client info')
    ip_list = re['ip'].split(',')
    if ip_client in ip_list:
        return 0
    return -1

def send_file(ip_client, data_unpack):
    hex_ip = util.get_ip_hex_format(ip_client)
    test_name = data_unpack['testname']
    test_type = util.get_test_type_by_name(config_name, test_name)
    result = data_unpack['result']
    log_name_local = log_dir + '/' + ip_client + test_name + '.log'
    log_name_local = log_name_local.encode('utf-8')
    log_name_remote = test_type + '_' + result + '_' + hex_ip + '_' + test_name + '.log'
    info = util.get_dict_from_config(config_name, 'ftp_server')
    ip = info['ip']
    usr = info['usr']
    psd = info['psd']
    dirname = info['dirname']
    util.send_file_to_webserver(ip, usr, psd, dirname, log_name_local, log_name_remote)

def get_next_cmd(list_tmp, ip_client, testobj, file_path):
    for (i,(k, v)) in enumerate(list_tmp):
        if k == global_var.GLOBAL_FUNCTION[ip_client]['testname']:
            testname = list_tmp[(i+1)][0]
            timeout = list_tmp[(i+1)][1]
            testcmd = testobj.get_testcmd(testname)
            status = 0
            if i == (len(list_tmp) - 2):
                status = 1
            else:
                status = 0
            info = [testname,timeout,testcmd,testobj,status,file_path]
            info_re = get_test_info(*info)
            global_var.GLOBAL_FUNCTION[ip_client] = info_re
            return info_re
    global_var.GLOBAL_FUNCTION[ip_client] = {'data':'on standby'}
    return {'data':'on standby'}

def get_test_info(*info):
    info_dict = {}
    info_dict['testname'] = info[0]
    info_dict['timeout'] = info[1]
    info_dict['testcmd'] = info[2]
    info_dict['test_type'] = info[3]
    info_dict['status'] = info[4]
    info_dict['file_path'] = info[5]
    return info_dict

def get_result(testobj, list_tmp, file_path, ip_client, data_unpack):
    if not global_var.GLOBAL_FUNCTION[ip_client].has_key('testname'):
        #当天第一次测试
        testname = list_tmp[0][0]
        timeout = list_tmp[0][1]
        testcmd = testobj.get_testcmd(testname)
        if len(list_tmp) == 1:
            status = 1
            info = [testname,timeout,testcmd,testobj,status,file_path]
            info_re = get_test_info(*info)
        else:
            status = 0
            info = [testname,timeout,testcmd,testobj,status,file_path]
            info_re = get_test_info(*info)
        global_var.GLOBAL_FUNCTION[ip_client] = info_re
        return info_re
    else:
        #查看从client收到的数据是否包含“result”，若包含则说明有log传过来。
        if data_unpack.has_key('result'):
            send_file(ip_client, data_unpack)
        #获取下次测试信息
        return get_next_cmd(list_tmp, ip_client, testobj, file_path)

def handle_board_data(data_unpack, *testobj_list):
    #判断连接上的client是不是待测试的板子，返回-1。
    #如果是而且client是第一次连接上来则初始化。
    ip_client = data_unpack['ip']
    if check(ip_client) == -1:
        return -1
    elif not global_var.GLOBAL_FUNCTION.has_key(ip_client):
        global_var.GLOBAL_FUNCTION[ip_client] = {'data':'on standby'}
    #tuple (int,int)
    #预定测试时间到达之后，改变client的状态。
    time_start = common_lib.get_start_test_time(config_name, 'start_test_time')
    if (datetime.now().hour,datetime.now().minute) == (time_start[0],time_start[1]) and \
            global_var.GLOBAL_FUNCTION[ip_client] == {'data':'on standby'}:
        testobj = testobj_list[0]
        global_var.GLOBAL_FUNCTION[ip_client] = {}
        global_var.GLOBAL_FUNCTION[ip_client]['test_type'] = testobj

    #当前没有到测试时间则返回给client值为{'data':'on standby'}。
    elif global_var.GLOBAL_FUNCTION[ip_client] == {'data':'on standby'}:
        return {'data':'on standby'}

    #传递下一个测试类型的测试信息给板子。
    elif global_var.GLOBAL_FUNCTION[ip_client]['status'] == 1 and \
            global_var.GLOBAL_FUNCTION[ip_client]['test_type'] != testobj_list[-1]:
        for i, v in enumerate(testobj_list):
            if v == global_var.GLOBAL_FUNCTION[ip_client]['test_type']:
                testobj = testobj_list[(i+1)]
                global_var.GLOBAL_FUNCTION[ip_client] = {}
                global_var.GLOBAL_FUNCTION[ip_client]['test_type'] = testobj
                break
    #全部测试信息都已经传递完毕，传递{'data':'on standby'},让它继续等待，下次测试到来
    elif global_var.GLOBAL_FUNCTION[ip_client]['test_type'] == testobj_list[-1] and \
            global_var.GLOBAL_FUNCTION[ip_client]['status'] == 1:
        global_var.GLOBAL_FUNCTION[ip_client] = {'data':'on standby'}
        return {'data':'on standby'}
    testobj = global_var.GLOBAL_FUNCTION[ip_client]['test_type']
    dict_tmp = testobj.get_testnames_timeout()
    list_tmp = dict_tmp.items()
    file_path = util.get_dict_from_config(config_name, 'download_file_server')
    return get_result(testobj, list_tmp, file_path, ip_client, data_unpack)
