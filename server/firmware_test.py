#!/usr/bin/python
#-*- coding: UTF-8 -*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.12.09
# Version : v1.1

import os
import time
import threading
import subprocess
import pexpect
from datetime import datetime
from util import util
from util import board_lib
from util import fwtest_lib
from util.pack import PackData
import global_var

config_name = 'config_server.ini'

def send_file(ip_client, file_log):
    ftp_info = util.get_dict_from_config(config_name, 'ftp_server')
    host = ftp_info['ip']
    usr = ftp_info['usr']
    psd = ftp_info['psd']
    dir_remote = os.path.join(ftp_info['dirname'][:-5], 'data')
    try:
        print host,usr,psd,dir_remote,file_log
        util.send_file_to_webserver(host, usr, psd, dir_remote, file_log, file_log)
    except:
        print 'send file to web failed'
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 110
    global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
    return 0


def fw_test(ip_client, sdk, sensor):
    """fw test"""
    list_process = ['syslogd','klogd','entropy','nm_init','ntpclient','octopus','alsad','rtspd',\
            'areceiver','aplayer','miniupnpd','sync_osd_time','doorkeeper','event_monitor','tuning-server','peacock']
    exec_cmd = ''
    if sdk == 'sdk-v1.2.1_rc2' and sensor == 'ov9715':
        exec_cmd = './testisp_v1.2.1_rc2 -c 9715.json\n'
    elif sdk == 'sdk-v1.2.1_rc2' and sensor == 'ov9750':
        exec_cmd = './testisp_v1.2.1_rc2 -c 9750.json\n'
    else:
        print 'no such sdk version or sensor!'
        return 102
    file_change = ''
    file_log = 'firmware_' + time.strftime('%Y%m%d---%H:%M:%S_') + sdk + '_' + sensor + '.log'
    print exec_cmd
    try:
        fout = open(file_log, 'w+')
        foo = pexpect.spawn('telnet ' + ip_client,timeout = 600, logfile = fout)
        time.sleep(5)
        foo.expect('login:')
        foo.send('root\n')
        foo.expect('~ #')
        foo.send('mount -t nfs -o nolock 10.0.10.24:/home/ipcam/nfs /mnt\n')
        foo.expect('~ #')
        foo.send('cd /mnt/fw\n')
        foo.expect('/mnt/fw #')
        for p in list_process:
            cmd = 'killall ' + p + '\n'
            foo.send(cmd)
            foo.expect('/mnt/fw #')
        foo.send(exec_cmd)
        foo.expect('/mnt/fw #')
        foo.send('exit\n')
    except Exception,e:
        print e
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 109
    finally:
        file_change = 'firmware_pass_' + time.strftime('%Y%m%d---%H:%M:%S_') + sdk + '_' + sensor + '.log'
        pos = 0
        for i in range(3):
            while True:
                pos = pos - 1
                try:
                    fout.seek(pos,2)
                    if fout.read(1) == '\n':
                        break
                except:
                    fout.seek(0,0)
                    break
            if 'fail' in fout.readline():
                file_change = 'firmware_fail_' + time.strftime('%Y%m%d---%H:%M:%S_') + sdk + '_' + sensor + '.log'
        foo.close()
        fout.close()
    os.rename(file_log, file_change)
    global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 3
    return send_file(ip_client, file_change)

def init_board(ip_client, sdk, sensor):
    path_current = os.getcwd()
    #build the linux.bin
    info_fwtest = util.get_dict_from_config(config_name, 'info_fwtest')
    path_image = info_fwtest['path_image']
    path_kernel_tree = info_fwtest['kernel_tree']
    path_vmlinuz = path_image + '/' + sdk + '/vmlinuz.img'
    path_rootfs = path_image + '/' + sdk + '/rootfs.bin'

    #copy image, rootfs and fw to code tree
    src_image_file = path_vmlinuz
    src_rootfs_file = path_rootfs
    src_fw_file = path_current + '/test_fw/mcu_fw.bin'
    dst_file = path_kernel_tree + '/image'
    re = subprocess.call(['cp', src_image_file, src_rootfs_file, src_fw_file, dst_file])
    if re != 0:
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 105

    #exec 'make pack' to generate linux.bin
    cmd = 'cd ' + path_kernel_tree + '; make pack'
    re = subprocess.call(cmd, shell = True)
    if re != 0:
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 106

    #copy linux.bin to test_fw
    cmd = 'cd ' + path_kernel_tree + '/image ; cp linux.bin ' + path_current + '/test_fw'
    subprocess.call(cmd, shell = True)
    if re != 0:
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 107

    #update image
    path_image = path_current + '/test_fw/linux.bin'
    if board_lib.check_board_on_line(ip_client) == 0:
        for i in range(3):
           if board_lib.update_image(ip_client, path_image) == 0:
                if board_lib.update_image(ip_client, path_image) == 0:
                    break
                elif i == 2:
                    global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
                    return 101
    else:
        global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
        return 100
    #ready to test
    global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 2
    #sleep wait the board reboot
    time1 = datetime.now()
    while True:
        time.sleep(5)
        if board_lib.check_board_on_line(ip_client) == 0:
            time.sleep(30)
            break
        time2 = datetime.now()
        if (time2-time1).seconds > 200:
            global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
            return 108
    #start fw test
    print 'fw test'
    return fw_test(ip_client, sdk, sensor)

def fw_init(ip_client, data):
    """init fw test
    fw status : 2 , ready to test
                1 , setting test environment
                0 , free
                3 , finish fw test
    """
    pd = PackData()
    local_path = 'test_fw'
    if not os.path.exists(local_path):
        os.mkdir(local_path)
    ip = data['ip']
    port = data['port']
    usr = data['usr']
    psd = data['psd']
    sdk = data['sdk_version']
    sensor = data['sensor']
    #str
    dir_path = data['dir_path']
    #list
    file_list = data['file_list']
    #fw file name
    filename_fw = data['filename_fw']

    fw_info = {'ip': ip, 'port': port, 'usr': usr, 'psd': psd, 'sdk': sdk, 'sensor': sensor,\
            'dir_path': dir_path, 'file_list': file_list, 'filename_fw' : filename_fw}
    #download file from web
    for f in file_list:
        if f == fw_info['filename_fw']:
            filename = 'mcu_fw.bin'
        else:
            filename = f
        if util.get_file_from_webserver(ip,usr,psd,local_path + '/%s'%filename,''.join([dir_path,'/',f])) == -1:
            print 'get file from webserver failed'
            global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 0
            return 111
    global_var.GLOBAL_FIRMWARE[ip_client]['status'] = 1
    #init board including make pack bin files,update image,
    return init_board(ip_client, sdk, sensor)

def handle_fw_data(command_name, data_unpack):
    if command_name == 1:
        ip_table = util.get_dict_from_config(config_name, 'table_fwtest')
        #get fw status,if status is 0,free and you can test.
        ip = ip_table[data_unpack['sensor']]
        print 'ip:',ip,data_unpack['sensor']
        status_fw = global_var.GLOBAL_FIRMWARE[ip]['status']
        if data_unpack.has_key('command'):
            command_fw = data_unpack['command']
            command_list = util.get_dict_from_config(config_name, 'command_list')['command']
            if command_fw in command_list:
                if command_fw == 'get_status':
                    send_data = {'data':status_fw}
                elif command_fw == 'check_online':
                    re = fwtest_lib.check_fw_board_online(ip)
                    if re == 0:
                        re = 'online'
                    else:
                        re = 'offline'
                    send_data = {'data':re}
                elif command_fw == 'get_table_fwtest':
                    send_data = {'data':fwtest_lib.get_table_ip_sensor(config_name, 'table_fwtest')}
            else:
                send_data = {'data':120}
        else:
            if status_fw == 0:
                re = fwtest_lib.check_fw_board_online(ip)
                if re == 'offline':
                    send_data = {'data':'offline'}
                else:
                    send_data = {'data':'OK'}
                    thread_fw_init = threading.Thread(target = fw_init, args = (ip, data_unpack))
                    thread_fw_init.start()
            else:
                send_data = {'data':'BUSY'}
    else:
        send_data = {'data':120}
    print 'send_data:',send_data
    return send_data

if __name__ == '__main__':

    ftp_info = util.get_dict_from_config(config_name, 'ftp_server')
    host = ftp_info['ip']
    usr = ftp_info['usr']
    psd = ftp_info['psd']
    file_log = 'error_code'
    dir_remote = os.path.join(ftp_info['dirname'][:-5], 'data')
    print host,usr,psd,dir_remote,file_log
    util.send_file_to_webserver(host, usr, psd, dir_remote, file_log)
