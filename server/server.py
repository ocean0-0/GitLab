#!/usr/bin/python
#-*- coding: UTF-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.12.29
# Version : v1.3

import os
import time
import copy
import socket
import multiprocessing
from datetime import datetime
from util import util
from util.board_lib import *
from util.common_lib import *
from util.fwtest_lib import *
from util.pack import PackData
import update_kernel
import firmware_test
import handle_function_test
from test_abstract import Test
import global_var

config_name = 'config_server.ini'
log_dir = 'log_dir'
__version__ = 'v1.3'

class FuncTestCase(Test):

    def get_testnames_timeout(self):
        re = {}
        testcases = util.get_dict_from_config(config_name, 'testlist')['function']
        testlist = testcases.split(',')
        for i,t in enumerate(testlist):
            re[t.split(':')[0]] = t.split(':')[1]
        return re

    def get_testname(self, testname):
        return testname

    def get_timeout(self, testname):
        for (k, v) in self.get_testname_timeout().items():
            if testname == k:
                return v
        return None

    def get_testcmd(self, testname):
        testcmds = util.get_dict_from_config(config_name, 'test_cmd')
        for (k, v) in testcmds.items():
            if k == testname:
                return v.split(',')
        return None

class PerformanceTestCase(Test):

    def get_testnames_timeout(self):
        re = {}
        testcases = util.get_dict_from_config(config_name, 'testlist')['performance']
        testlist = testcases.split(',')
        for i,t in enumerate(testlist):
            re[t.split(':')[0]] = t.split(':')[1]
        return re

    def get_testname(self, testname):
        return testname

    def get_timeout(self, testname):
        for (k, v) in self.get_testname_timeout().items():
            if testname == k:
                return v
        return None

    def get_testcmd(self, testname):
        testcmds = util.get_dict_from_config(config_name, 'test_cmd')
        for (k, v) in testcmds.items():
            if k == testname:
                return v.split(',')
        return None

testobj_list = [PerformanceTestCase(),FuncTestCase()]

from twisted.internet import defer,threads
from twisted.internet.protocol import Protocol,ServerFactory

def update_kernel():
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

def init_fw():
    ip_table = util.get_dict_from_config(config_name, 'table_fwtest')
    for ip in ip_table.values():
        global_var.GLOBAL_FIRMWARE[ip] = {}
        global_var.GLOBAL_FIRMWARE[ip]['status'] = 0

def parse_data(data):
    pd = PackData()
    data_unpack = pd.get_body(data)
    command = pd.get_command_id(data)
    command_type = command >> 16
    command_name = command & 0x0ffff
    return command_type, command_name, data_unpack

import time
from threading import current_thread
#处理函数
def handle_data(msg):
    command_type, command_name, data_unpack = parse_data(msg)
    if command_type == 1:
        re = util.get_dict_from_config(config_name, 'web_server_cmd')
        cmd_list = re['cmd_list'].split(',')
        if (type(data_unpack) is dict) and (set(data_unpack.keys()) <= set(cmd_list)):
            return {'result':'nonsupport'}
        else:
            return {'result':'fail'}
    elif command_type == 2:
        re = handle_function_test.handle_board_data(data_unpack,
                *testobj_list)
        tmp = copy.deepcopy(re)
        if tmp.has_key('test_type'):
            del tmp['test_type']
        re_tmp = {}
        re_tmp[data_unpack['ip']] = tmp
        return re_tmp
    elif command_type == 3:
        re = firmware_test.handle_fw_data(command_name, data_unpack)
        return {'status':re}

class TestProtocol(Protocol):

    #当连接产生时被调用的方法。
    def connectionMade(self):
        peer = self.transport.getPeer()
        print 'client:',(peer.port, peer.host)

    #收到数据时会被调用的方法
    def dataReceived(self, data):
        d = threads.deferToThread(handle_data,data)
        d.addCallbacks(self.write, self.handle_err)

    def handle_err(self, result):
        print 'My error:', result

    def write(self, data):
        print data
        pd = PackData()
        data = pd.pack_data('0.1', 0xffffffff, data)
        self.transport.write(data)

    #连接关闭时会被调用的方法
    def connectionLost(self, reason):
        print 'connection lost:',self.transport.getPeer().host
        print 'lost reason',reason

class TestProtocolFactory(ServerFactory):

    protocol = TestProtocol

if __name__ == '__main__':

    from twisted.internet import reactor
    reactor.callWhenRunning(init_fw)
    factory = TestProtocolFactory()
    reactor.listenTCP(20000,factory)
    reactor.run()

    #start process to update kernel(master)
    #update_p = multiprocessing.Process(target=test.update_kernel)
    #update_p.start()
