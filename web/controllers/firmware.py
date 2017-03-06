#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import re
import web
import sys
import json
import value
import threading
import ConfigParser

from web import form

sys.path.append('..')
from settings import render
from utility.scan import *
from utility.date import *
from tool.firmware import *

g_mutex = threading.Lock()

# get info from base.conf
cf = ConfigParser.ConfigParser()
cf.read('base.conf')

# get server info
g_server_ip = cf.get('server', 'server_ip')
g_server_port = int(cf.get('server', 'server_port'))

# get client info
g_ip = cf.get('client', 'ip')
g_port = int(cf.get('client', 'port'))
g_usr = cf.get('client', 'usr')
g_psd = cf.get('client', 'psd')

# Firmware
LOG_PATH = 'data/'
FIRMWARE_LOG_FORMAT = 'firmware*.log'
g_exit = 0
g_mail_receiver = 'linda_bao@realsil.com.cn'

# Form
vtime = form.regexp(r"^(0\d{1}|1\d{1}|2[0-3]):([0-5]\d{1})$", "format like this 08:50")

register_form = form.Form(
    form.Textbox("time", vtime, description="time:"),
    form.Button("submit", type="submit", description="Register"),
)

firmware_form = form.Form(
    form.Dropdown("Sensor", ['ov9715'], description="SensorType"),
    form.Dropdown("SDK", ['sdk-v1.0.3', 'sdk-v1.1-rc1'], description="SDK-version"),
    form.Button("GetList",type="button",value="Obtain"),
    form.Textbox("Email",
        form.notnull,
        form.regexp(r".*@.*", "must be a valid email address"),
        placeholder="Your email address"),
)

class Firmware:
    """firmware test"""

    def GET(self):
        firmware_test_info = firmware_form()
        return render.firmware(firmware_test_info)

    def POST(self):
        firmware_test_info = firmware_form()
        start_time = ''
        ipcam_status = ''
        if not firmware_test_info.validates():
            return render.firmware(firmware_test_info)
        else:
            #global g_mutex
            g_mutex.acquire()
            global g_mail_receiver
            # upload fw.bin
            #Storage
            fw_bin = web.input(myfile={})
            if not os.path.exists('firmware'):
                os.system('mkdir firmware')
            else:
                # storage fw.bin
                filedir = os.getcwd() + '/firmware'
                filepath = ''
                filename = ''
                file_list = []
                result = ''
                if 'myfile' in fw_bin:
                    filepath = fw_bin.myfile.filename.replace('\\','/')
                    filename = filepath.split('/')[-1]
                    fw_dir  = filedir +'/' +filename
                    fout = open(fw_dir, 'w')
                    fout.write(fw_bin['myfile'].value)
                    fout.close()
                    file_list.append(filename)
                data_fw = {'ip': g_ip, 'port': g_port, 'usr': g_usr, 'psd': g_psd,\
                           'sdk_version': firmware_test_info.d.SDK.encode('utf-8'), \
                           'sensor': firmware_test_info.d.Sensor.encode('utf-8'),\
                           'dir_path': filedir,'file_list': file_list,\
                           'filename_fw': fw_bin['myfile'].filename
                           }
                send_request(g_server_ip, g_server_port, data_fw)
                mail_re = firmware_test_info.d.Email.encode('utf-8')
                if not (mail_re == g_mail_receiver ):
                    g_mail_receiver = mail_re
                g_mutex.release()
            return render.firmware(firmware_test_info)


class FirmwareTestStatus:
    """get current test status for ajax in firmware.html
    """
    def GET(self):
        online_ov9715 = value.online_ov9715
        online_ov9750 = value.online_ov9750
        g_status_ov9715 = value.g_status_ov9715
        g_status_ov9750 = value.g_status_ov9750
        if (online_ov9750 == "offline"):
            status_ov9750 = online_ov9750
        else:
            status_ov9750 = g_status_ov9750
        if (online_ov9715 == "offline"):
            status_ov9715 = online_ov9715
        else:
            status_ov9715 = g_status_ov9715
        info = {'ov9715':[status_ov9715], \
                'ov9750':[status_ov9750]
               }
        return json.dumps(info)

class FirmwareLogCheck:
    """ check firmware*.log exist or not for ajax in firmware.html
    """
    def GET(self):
        file_list = []
        j_result = ''
        file_dir = LOG_PATH
        option = FIRMWARE_LOG_FORMAT
        file_list = glob.glob(file_dir + option)
        if(file_list != []):
            # handle the log file for mail attach
            attach_dir = file_list[0]
            attach_name_index = attach_dir.find('firmware')
            attach_name = attach_dir[attach_name_index:]
            attach_result_index = attach_name_index + len('firmware_')
            test_result = attach_dir[attach_result_index:attach_result_index+4]
            subject = 'Firmware test report_'+test_result
            content = 'Your test finished.\n' + 'Check the attach when you want to get the detail of the report.'
            # mail to notice the testor with log in attach
            mail(g_mail_receiver, subject, content, attach_dir, attach_name)
            # find the log and classify it 
            result=file_search(file_dir,option)
        else:
            result = 0
        j_result = {'log_info': result}
        return json.dumps(j_result)

class FirmwareBoardList:
    """ get firmware board list for ajax in firmware.html
    """
    def GET(self):
        board_list = get_firmware_board_list(g_server_ip, g_server_port)
        return json.dumps(board_list)
