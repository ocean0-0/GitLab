# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.09.26


import json
import commands
import platform
import requests

from requests.auth import HTTPDigestAuth

usr = 'admin'
psd = '123456'

def check_board_on_line(ip):
    cmd = ''
    if platform.system() == 'Linux':
        cmd = 'ping -c 2 ' + str(ip)
    elif platform.system() == 'Windows':
        cmd = 'ping -n 2 ' + str(ip)
    status,output = commands.getstatusoutput(cmd)
    if status == 0:
        return 0
    else:
        return -1

def get_board_info(ip):
    #sdkVersion: v1.0.3-rc1\n
    #macAddr: 00-E0-4C-05-00-30
    #protocol: static
    #encryption: OPEN
    #bssid: 00:00:00:00:00:00
    #state: diabled
    #dns1: 10.0.0.1
    #buildTime: PREEMPT Wed Sep 7 15:19:14 CST 2016
    #ipAddr: 10.0.2.54
    #upTime: 0day:19h:50m:32s
    #fwVersion: 0002007b 00060000, essid: "00-00-00-00-00-00", dns2: 0.0.0.0
    #subnetMask: 255.255.240.0
    #gateway: 10.0.0.1
    #uuid: 00000000000000000000
    url = 'http://' + str(ip) + '/cgi-bin/status.cgi'
    data = {'command':'getStatus','data':[]}
    r = requests.post(url, data = json.dumps(data), auth = HTTPDigestAuth(usr, psd))
    try:
        re = r.json()
    except Exception,e:
        print e
        return -1
    return re

def update_image(ip, filename):
    #64kb
    size = 64
    count = 0
    url = 'http://'+ ip + '/cgi-bin/firmware.cgi'
    try:
        with open(filename, 'r') as fd:
            while True:
                count += 1
                file_slice = fd.read(1024 * size)
                if file_slice != '':
                    r = requests.post(url, data = file_slice, auth = HTTPDigestAuth(usr, psd), stream = True, timeout = 10)
                    try:
                        re = r.json()
                        print re
                    except Exception,e:
                        print e
                        return -1
                    if re['status'] != 'succeed':
                        print re['status']
                        return -1
                    print re['status'],count
                else:
                    break
    except Exception,e:
        print e
        return -1
    return 0


if __name__ == '__main__':
    #print check_board_on_line('10.0.10.26')
    update_image('10.0.10.74', '../linux_function.bin')
