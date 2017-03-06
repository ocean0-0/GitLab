
#!/usr/bin/python
# coding: UTF-8

import os
import sys
import json
import time
import pexpect
import urllib2
import subprocess
from datetime import datetime
from util import util
from util.board_lib import *
from cgi_test import cgi_main

count = 0
realm = 'realsil'

def warninfo(info):
    print('Warn -> ' + info)

def jsons2dict(cmdJsons):
    cmd_dict = {}
    try:
        cmd_dict = json.loads(cmdJsons)
    except Exception as inst:
        warninfo(type(inst))
        warninfo(inst.args)
        warninfo(inst)
    if not isinstance(cmd_dict, dict):
        self.warninfo('response is not a dict: %s', cmdJsons)
    return cmd_dict

def resp_checkstatus(respDict):
    respDict = jsons2dict(respDict)
    if respDict == False:
        return False
    elif not isinstance(respDict, dict):
        return False
    else:
        if respDict.has_key('status'):
            status_value = respDict['status']
            if 'succeed' == status_value:
                return True
            else:
                self.warninfo('response failed: %s' % (respDict['reason']))
                return False
        else:
            self.warninfo('response invalid')
            return False
    return False

def upload_file(config_name, filename, size, client_ip):
    """upload file"""
    info = util.get_dict_from_config(config_name, 'client info')
    usr = info['usr']
    psd = info['psd']
    url_ip = client_ip
    url_cgi = 'http://' + url_ip + '/' + 'cgi-bin/firmware.cgi'
    fp = open(filename, 'rb')
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(self.realm, url_cgi, usr, psd)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPDigestAuthHandler(passman)))
    while(True):
        file_data = fp.read(1024 * size)
        if(file_data == ''):
            fp.close()
            break
        request = urllib2.Request(url_cgi, file_data)
        try:
            res = urllib2.urlopen(request)
            count += 1
        except Exception,e:
            time.sleep(2)
            print e
            break
        else:
            res = res.read()
            if len(res) == 0:
                break
            if  resp_checkstatus(res) == False:
                print 'update kernel failed!'
                break
            else:
                print 'success ' + str(count)
    count = 0
    print 'success'

def makeSDK(config_name, filename, cgi_flag, ip_client = '', flag = True):
    print cgi_flag,flag
    send_cmd = 'exit'
    proj = ''
    if cgi_flag == True:
        proj = 'image_cgi'
    else:
        proj = 'image_info'
    info = util.get_dict_from_config(config_name,proj)
    src_host = info['src_host']
    src_pwd = info['src_pwd']
    src_path = info['src_path']
    src_user = info['src_user']
    if cgi_flag == False and flag == True:
        init_cmd = 'python setup_after.py;cd ipcam_latest;repo sync;\
                    make clean > make.log;make >> make.log;make pack;exit'
    elif cgi_flag == True and flag == True:
        info = util.get_dict_from_config(config_name,'image_cgi')
        src_path = info['src_path']
        init_cmd = 'cd ipcam_cgi;\
                    rm target/image/*;make clean > make.log;repo sync;make >> make.log;\
                    make pack >> make.log;exit;'
        send_cmd = 'exit'
    elif cgi_flag == False and flag == False:
        print 'setup_test:',ip_client
        send_cmd= 'python setup_before.py; \
                   cd ipcam_latest/users/ipcam/linux_test/testSD/client; \
                   python setup.py {ip_client}; \
                   cd -;cd ipcam_latest;rm target/image/*;make >> make.log;\
                   make pack;cd -;python setup_after.py;exit'.format(ip_client=ip_client)

    cmd = r"""
            expect -c "
            spawn ssh {src_user}@{src_host}
            expect \"password:\"
            send \"{src_pwd}\r\"
            set timeout 60000
            expect shanjian_fei@*
            send \"{cmd}\r\"
            expect eof
            "
    """.format(src_user=src_user,src_host=src_host,src_pwd=src_pwd,cmd=init_cmd if flag else send_cmd)
    p  = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (output, err) = p.communicate()
    if flag == False:
        scp_cmd = r"""
                expect -c "
                spawn scp {src_user}@{src_host}:{src_path} {filename}
                expect \"password:\"
                send \"{src_pwd}\r\"
                set timeout 600
                expect eof
                "
        """.format(src_user=src_user,src_host=src_host,src_pwd=src_pwd,src_path=src_path,filename=filename)
        p  = subprocess.Popen(scp_cmd , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

def start_update(config_name, cgi_flag, *ip_list):
    if cgi_flag == True:
        filename = 'linux_cgi.bin'
    else:
        filename = 'linux_function.bin'
    print filename
    makeSDK(config_name, filename, cgi_flag, flag = True)
    for ip in ip_list:
        if os.path.exists(filename) and cgi_flag == False:
            os.remove(filename)
        if check_board_on_line(ip) != 0:
            time.sleep(50)
        if check_board_on_line(ip) == 0:
            print ip
            makeSDK(config_name, filename, cgi_flag, ip, flag = False)
            if os.path.getsize(filename) > 1000:
                for i in range(3):
                   if update_image(ip, filename) == 0:
                        if update_image(ip, filename) == 0:
                            break
                time.sleep(10)
                time1 = datetime.now()
                while True:
                    time.sleep(10)
                    time2 = datetime.now()
                    if (time2 - time1).seconds >= 100:
                        print ip,' had changed!'
                        return -1
                    if check_board_on_line(ip) == 0:
                        config_cgi = os.path.join(os.getcwd(),'cgi_test/config.ini')
                        log_name = 'reboot.log'
                        cgi = cgi_main.CGI()
                        cgi.set_ip(ip)
                        cgi.set_testname('reboot')
                        cgi.set_logname(log_name)
                        cgi.set_config_name(config_cgi)
                        cgi.cgi_main()
                        os.remove(log_name)
                        break
if __name__ == '__main__':
    d = ['10.0.10.74']
    #makeSDK('config_server.ini', False, ip_client = '10.0.10.76', flag = False)
    #upload_file('config_server.ini', 'linux.bin', 64, '10.0.10.76'):
    start_update('config_server.ini', False, *d)
