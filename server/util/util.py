# !/usr/bin/env python
# -*-coding: UTF-8-*-
# Author: Shanjian Fei <shanjian_fei@realsil.com.cn>
# Date: 2016.12.22
# Version: v1.2

import os
import sys
import time
import commands
import ConfigParser
from ftplib import FTP
from datetime import datetime

def finish():
    sys.exit(0)

def get_current_time():

    """get system time
       parttern:2016-01-21  13:11:01
    """
    return time.strftime('%Y-%m-%d---%H:%M:%S')

def get_ip_hex_format(ip):
    ip = ip.split('.')
    result = ''
    res = ''
    for i in range(len(ip)):
        result = result + str(hex(int(ip[i])))
    result = result.split('0x')
    for i in range(len(result)):
        if result[i] != '':
            if len(result[i]) == 1:
                result[i] = '0' + str(result[i])
            res = res + result[i]
    res = '0x' + res
    return res

def send_file_to_webserver(host, usr, psd, dirname, localfilename, remotefilename):
    """ send file by ftp
        need ip,usr,psd,dirname,urlweb
    """
    year = datetime.now().year
    month = datetime.now().month
    if month < 10:
        month = '0' + str(month)
    day = datetime.now().day
    if day < 10:
        day = '0' + str(day)
    remotedir = dirname + '/' + str(year) +str(month) + str(day)
    f = FTP(host)
    f.login(usr,psd)
    try:
        f.cwd(remotedir)
    except Exception,e:
        try:
            f.mkd(remotedir)
        except Exception,e:
            print "Change directory failed!"
    f.pwd()
    fd = open(localfilename,'rw')
    f.storlines("STOR %s"%(remotedir + '/' + remotefilename),fd)
    fd.close()
    f.quit()

def get_file_from_webserver(host, usr, psd, localfilename, remotefilename):
    """get test file from web server by ftp
       need ip,usr,psd,dirname,filename
    """
    path,file_name = os.path.split(remotefilename)
    print host, usr, psd, localfilename, remotefilename,path,file_name
    try:
        f = FTP(host)
    except Exception,e:
        print 'cannot reach "%s"'%host
        print e
        return -1
    try:
        f.login(usr,psd)
    except Exception,e:
        print 'ERROR:count not log in:',e
        return -1
    try:
        f.cwd(path)
    except Exception,e:
        print e
        print 'ERROR:no such directory!'
        return -1
    #f.dir()
    fd = open(localfilename,'wb')
    f.retrbinary('RETR %s'%(file_name),fd.write,1024)
    fd.close()
    f.quit()

def get_dict_from_config(config_name, proj_name):
    """get dict by section from config.ini"""
    re = {}
    config = ConfigParser.ConfigParser()
    config.read(config_name)
    if config.has_section(proj_name):
        options = config.options(proj_name)
        for the_key in options:
            re[the_key] = config.get(proj_name, the_key)
    return re

def kill_process(process_name):
    cmd = 'killall ' + process_name
    os.system(cmd)

def get_pid(name_process):
    import commands
    list_info = commands.getoutput('ps aux').split('\n')
    for info in list_info:
        if name_process in info:
            info = info.split()
            return int(info[1])
    return None

def get_test_type_by_name(config_name, test_name):
    re = get_dict_from_config(config_name , 'testlist')
    for k in re.keys():
        if test_name in re[k]:
            return k
    return None

if __name__ == '__main__':
    print get_pid('python')
    print get_test_type_by_name('../config_server.ini','testaudio')
    print get_test_type_by_name('../config_server.ini','top')
    send_file_to_webserver('172.29.40.184', 'rspcwiki', '_Rspcwiki121', '/home/rspcwiki/Desktop/web/data', 'util.py', 'util.py')
    #print get_dict_from_config('../config_server.ini', 'command_list')
    #get_file_from_webserver('172.29.40.183','rspcmantis','_Rspcmantis121','arr','/home/rspcmantis/Desktop/web/RTS3901_FW_OV9715_V0000.002e.bin')
    #get_file_from_webserver('172.29.40.183','rspcmantis','_Rspcmantis121','arr','/home/rspcmantis/Desktop/web/RTS3901_OV9715_V0002.007c.bin')
