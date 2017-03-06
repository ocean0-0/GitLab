# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Shanjian Fei<shanjian_fei@realsil.com.cn>
# Date: 2016.12.22
# Version: v1.2

import sys
import json
import time
import types
import urllib2
import ConfigParser
from itertools import *

class IPCTest(object):
    def __init__(self, ip, usr, psd, log_name, config_name):
        self.log_name = log_name
        self.ip = ip
        self.usr = usr
        self.psd = psd
        self.config_name = config_name
        self.count = 0

    def warninfo(self, info):
        print('Warn -> ' + str(info))

    def get_dict_from_config(self, config_name, proj_name):
        """get dict by section from config.ini"""
        re = {}
        config = ConfigParser.ConfigParser()
        config.read(config_name)
        if config.has_section(proj_name):
            options = config.options(proj_name)
            for the_key in options:
                re[the_key] = config.get(proj_name, the_key)
        return re

    def dict2jsons(self, cmdDict):
        cmd_str = ''
        if isinstance(cmdDict, str):
            cmd_str = cmdStr
        else:
            try:
                cmd_str = json.dumps(cmdDict)
            except:
                self.warninfo('convert to json fail: %s' % (cmdDict))
        return cmd_str

    def jsons2dict(self, cmdJsons):
        cmd_dict = {}
        try:
            cmd_dict = json.loads(cmdJsons)
        except Exception as inst:
            self.warninfo(type(inst))     # the exception instance
            self.warninfo(inst.args)      # arguments stored in .args
            self.warninfo(inst)           # __str__ allows args to be printed directly
        if not isinstance(cmd_dict, dict):
            self.warninfo('response is not a dict: %s', cmdJsons)
        return cmd_dict

    def send_request(self, cgi_path, request, timeoutsec = 20):
        self.count += 1
        request = self.dict2jsons(request)
        response_str = self.query(cgi_path, request, timeoutsec)
        if response_str == -1:
            return -1
        response_dict = self.jsons2dict(response_str)
        data = str(self.count) + str(request) + str(response_dict) + '\n'
        with open(self.log_name, 'a+') as f:
            f.write(data)
        if self.check_result(response_dict) == False:
            return -1
            #sys.exit(0)
        return 0

    def get_cgi_path(self, test_name):
        info = self.get_dict_from_config(self.config_name, 'cgi_path')
        if info.has_key(test_name):
            return info[test_name]
        else:
            return ''

    def get_requests(self, test_name):
        info = self.get_dict_from_config(self.config_name, 'requests')
        if info.has_key(test_name):
            return eval(info[test_name].strip())
        else:
            return []

    def handle_common_cmd(self, cgi_path, request):
        value_tmp = []
        if request['command'].find('set') == 0:
            if request.has_key('data'):
                data = request['data']
                if type(data) == list:
                    for d in data:
                        rq = {'data':[d]}
                        rq['command'] = request['command']
                        if self.send_request(cgi_path,rq) == -1:
                            return -1
                else:
                    keys = data.keys()
                    for k in keys:
                        value_tmp.append(data[k])
                    for p in product(*value_tmp):
                        data_tmp = {}
                        for j,k in enumerate(keys):
                            data_tmp[k] = p[j]
                        rq = {'data':data_tmp}
                        rq['command'] = request['command']
                        if self.send_request(cgi_path,rq) == -1:
                            return -1
            else:
                if self.send_request(cgi_path,request) == -1:
                    return -1
        else:
            if self.send_request(cgi_path,request) == -1:
                return -1

    def handle_stream_cmd(self, cgi_path, request):
        data = request['data']
        for s in request['stream']:
            value_tmp = []
            if request['command'].find('set') == 0:
                keys = data.keys()
                for k in keys:
                    value_tmp.append(data[k])

                for p in product(*value_tmp):
                    data_tmp = {}
                    for j,k in enumerate(keys):
                        data_tmp[k] = p[j]
                    rq = {'command':'setParam','stream':s,'data':data_tmp}
                    if self.send_request(cgi_path,rq) == -1:
                        return -1
            else:
                rq = request
                rq['stream'] = s
                if self.send_request(cgi_path,rq) == -1:
                    return -1

    def main(self, test_name):
        requests = self.get_requests(test_name)
        cgi_path = self.get_cgi_path(test_name)
        for request in requests:
            if request.has_key('stream'):
                if self.handle_stream_cmd(cgi_path,request) == -1:
                    return -1
            else:
                if self.handle_common_cmd(cgi_path,request) == -1:
                    return -1

    def query(self, cgi_path, request, timeoutsec):
        url_cgi = 'http://' + self.ip + cgi_path
        content = ''
        try:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password('realsil', self.ip, self.usr, self.psd)
            urllib2.install_opener(urllib2.build_opener(urllib2.HTTPDigestAuthHandler(passman)))
            request = urllib2.Request(url_cgi, request)
            response = urllib2.urlopen(request, timeout=timeoutsec)
            content = response.read()
        except Exception,e:
            data = 'error:' + str(e) + '\n'
            with open(self.log_name, 'a+') as f:
                f.write(data)
            return -1
        return content

    def check_result(self, result):
        if isinstance(result, dict) and result.has_key('status'):
            status = result['status']
            if 'succeed' == status:
                return True
            else:
                return False
        else:
            return False

if __name__ == '__main__':
    test = RIpCam('','','','','')
    print test.get_requests('isp')
