# -*- coding:utf-8 -*-
#!/usr/bin/python

import web
import sys
import time
import signal
import threading
import ConfigParser

import value
from tool.firmware import *
import url

sys.path.append('./controllers')
urls = url.urls
app = web.application(urls, globals())

g_exit = 0

# get info from base.conf
cf = ConfigParser.ConfigParser()
cf.read('base.conf')

# get server info
g_server_ip = cf.get('server', 'server_ip')
g_server_port = int(cf.get('server', 'server_port'))

def process_signal(sig, frame):
    global g_exit
    g_exit = 1
    print 'get signal'
    app.stop()

def firmware_status_listen():
    while True:
        # check online
        value.online_ov9715 = check_firmware_board_online('ov9715',g_server_ip, g_server_port)
        value.online_ov9750 = check_firmware_board_online('ov9750',g_server_ip, g_server_port)
        # check status
        value.g_status_ov9715 = get_firmware_board_status('ov9715',g_server_ip, g_server_port)
        value.g_status_ov9750 = get_firmware_board_status('ov9750',g_server_ip, g_server_port)
        time.sleep(2)
        if g_exit:
            break

# self defined notfound function
def notfound():
    return web.notfound("No such page, please contact with tristan_fei@realsil.com.cn!")

if __name__ == "__main__":
    app.notfound = notfound
    signal.signal(signal.SIGINT, process_signal)
    td  = threading.Thread(target=firmware_status_listen)
    td.start()
    app.run()
    td.join()
    exit(0)
