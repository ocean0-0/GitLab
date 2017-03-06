# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: shanjian_fei <shanjian_fei@realsil.com.cn>
# Date: 2016.12.22
# Version: v1.2

import time
import os
import sys
import pexpect
import subprocess
sys.path.append('..')
from util import util
from util.smtp import SendMail
from datetime import datetime

config_path = '../config_server.ini'

def check_compile_result(path):
    info = util.get_dict_from_config(config_path,'image_info')
    src_host = info['src_host']
    src_pwd = info['src_pwd']
    src_path = info['src_path']
    src_user = info['src_user']
    cmd_master = 'cd ' + path + ';' \
                       + 'repo sync;' \
                       + 'make clean > make.log;' \
                       + 'make V=1 >> make.log 2>&1'
    path_current = os.getcwd()
    cmd = r"""
            expect -c "
            spawn ssh {src_user}@{src_host}
            expect \"password:\"
            send \"{src_pwd}\r\"
            set timeout 60000
            expect shanjian_fei@*
            send \"{cmd}\r\"
            send \"scp make.log ipcam@172.29.43.31:{path}\r\"
            expect \"password:\"
            send \"ipcam-test\r\"
            expect shanjian_fei@*
            send \"exit\r\"
            expect eof
            "
    """.format(src_user=src_user,src_host=src_host,src_pwd=src_pwd,cmd=cmd_master,path=path_current)
    p  = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (output, err) = p.communicate()

    cmd = 'tail -n 100 make.log > check_compile.log'
    os.system(cmd)
    with open('check_compile.log','r') as f:
        for line in f.readlines():
            if ' Error ' in line or ' error ' in line:
                return -1
    return 0

def handle_compile_result(path):
    info = util.get_dict_from_config(config_path, 'ftp_server')
    ip = info['ip']
    usr = info['usr']
    psd = info['psd']
    dirname = info['dirname']
    log_name = path.split('-')[-1]
    if check_compile_result(path) == 0:
        time_now = util.get_current_time()
        remote_file = 'compile_pass_' + str(time_now) + '_' + log_name + '.log'
        local_file = 'check_compile.log'
        #os.system('cp ' + local_file + ' ' + remote_file)
        util.send_file_to_webserver(ip,usr,psd,dirname,local_file,remote_file)
    else:
        time_now = util.get_current_time()
        remote_file = 'compile_fail_' + str(time_now) + '_' + log_name + '.log'
        local_file = 'check_compile.log'
        #os.system('cp ' + local_file + ' ' + remote_file)
        util.send_file_to_webserver(ip,usr,psd,dirname,local_file,remote_file)

def get_test_time_range():
    info = util.get_dict_from_config(config_path, 'check_compile')
    start_time = int(info['start_time'])
    end_time = int(info['end_time'])
    return start_time,end_time

def main():
    start_time,end_time = get_test_time_range()
    path = ''
    while True:
        time.sleep(10)
        if start_time < datetime.now().hour < end_time:
            if datetime.now().minute == 0:
                path = 'ip_camera_master'
                handle_compile_result(path)
                time.sleep(50)
            elif datetime.now().minute == 20:
                path = 'ip_camera_release1.0'
                handle_compile_result(path)
                time.sleep(50)
            elif datetime.now().minute == 40:
                path = 'ip_camera_release1.1'
                handle_compile_result(path)
                time.sleep(50)


if __name__ == '__main__':
    #handle_compile_result()
    print get_test_time_range()
    #main()
