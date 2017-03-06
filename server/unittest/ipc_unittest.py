#! /usr/bin/python2.7
#-*-coding:utf-8
#Date               : 2016.08.02
#Author             : Shanjian Fei
#Mail               : <shanjian_fei@realsil.com.cn>

import sys
sys.path.append('..')
import util.db as db
from util.board_lib import *
from util.common_lib import *
import util.fwtest_lib
from socket_server import TCPServerSocket
import os
from ftplib import FTP
from datetime import datetime
import shutil
import sqlite3
import unittest
import multiprocessing


def create_table(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''CREATE TABLE board
                (id integer primary key autoincrement,
                 ip                 text,
                 status             text,
                 start              text,
                 testlist           text,
                 nexttest           text,
                 testcmd            text,
                 tested             text,
                 ftp_server         text,
                 extra_ftp_server   text,
                 extra_testlist     text,
                 extra_tested       text,
                 extra_nexttest     text,
                 extra_testcmd      text,
                 extra_flag         text);''')
    conn.execute("INSERT INTO board (id,ip,start,status,testlist,nexttest,testcmd,tested,\
            ftp_server,extra_ftp_server,extra_testlist,extra_tested,extra_nexttest,extra_testcmd,extra_flag) \
            VALUES (1,'10.0.10.27', '(10,11)', '3', 'hotplug_test:10,top:20' ,'8','a 1,b 3,c 4','hotplug',\
            '{host:10.0.10.24,usr:ipcam,psd:123}','{host:10.0.10.24,usr:ipcam,psd:123}',\
            '[a,b,c,d]','a','b','test b','1' )");
    conn.commit()
    conn.close()

def create_fw_table(db_name):
    db.create_fw_table(db_name, 'fwboard')

class DBUnitTest(unittest.TestCase):
    def setUp(self):
        self.board_name = 'board'
        self.db_name = 'ipcamtest.db'

    def test_create_db_table(self):
        db.create_table(self.db_name,self.board_name)
        self.assertTrue(os.path.exists(self.db_name))
        conn = sqlite3.connect(self.db_name)

        self.assertTrue(conn.execute('''select * from %s;'''%self.board_name))
        conn.close()

    def test_create_fw_table(self):
        asrt = ''
        table_name = 'fwtest'
        db.create_fw_table(self.db_name, table_name)
        self.assertTrue(os.path.exists(self.db_name))
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT name FROM sqlite_master WHERE type = 'table';''')
        re = cursor.fetchall()
        for i in re:
            if table_name in i:
                asrt = True
                break
            asrt = False
        self.assertTrue(asrt)
        cursor.execute("select * from %s;"%table_name)
        col_name_list = [tuple[0] for tuple in cursor.description]
        conn.close()
        self.assertTrue('ip' in col_name_list)
        self.assertTrue('sensor' in col_name_list)
        self.assertTrue('status' in col_name_list)

    def test_remove_db_table(self):
        self.test_create_db_table()
        #try:
        #    db.remove_table('ipcam.db')
        #    self.assertTrue(False)
        #except sqlite3.OperationalError:
        #    self.assertTrue(True)
        db.remove_table(self.db_name,self.board_name)
        conn = sqlite3.connect(self.db_name)
        try:
            conn.execute('''select * from %s;'''%self.board_name)
            self.assertTrue(False,'remove table failed!')
        except Exception,e:
            conn.close()
            self.assertTrue(True)

    def test_insert(self):
        self.test_create_db_table()
        db.insert_info(self.db_name,self.board_name,ip = '10.0.10.27')
        conn = sqlite3.connect(self.db_name)
        cursor = conn.execute('''select ip from %s;'''%self.board_name)
        for c in cursor:
            self.assertEqual('10.0.10.27',c[0])
        conn.close()

    def test_del(self):
        self.test_insert()
        conn = sqlite3.connect(self.db_name)
        db.del_from(self.db_name,self.board_name,1)
        cursor = conn.execute('''select id from %s;'''%self.board_name)
        for c in cursor:
            self.assertNotEqual(1,c[0])
        conn.close()

    def test_update(self):
        self.test_insert()
        conn = sqlite3.connect(self.db_name)
        db.update(self.db_name,self.board_name,1,ip = '10.0.10.28')
        cursor = conn.execute('''select ip from %s;'''%self.board_name)
        for c in cursor:
            self.assertEqual('10.0.10.28',c[0])
        conn.close()

    def test_find(self):
        self.test_insert()
        conn = sqlite3.connect(self.db_name)
        ip = db.find(self.db_name,self.board_name,1,'ip')
        self.assertEqual(ip,'10.0.10.27')
        conn.close()

    def test_add_column(self):
        self.test_insert()
        db.add_column(self.db_name,self.board_name,'test_column')
        columns = db.get_allcolumn(self.db_name,self.board_name)
        art = False
        for c in columns:
            if c == 'test_column':
                art = True
                break
        self.assertTrue(art)

    #socket server
    def test_check_board_status(self):
        ss = TCPServerSocket('../config_server.ini')
        re = ss.check_board_status('10.0.10.27')
        self.assertTrue(isinstance(re,dict))
        self.assertEqual(re['ip'],'10.0.10.27')
        os.remove(self.db_name)
        create_table(self.db_name)
        re = ss.check_board_status('10.0.10.27')
        self.assertTrue(isinstance(re,dict))
        self.assertEqual(re['ip'],'10.0.10.27')
        self.assertEqual(re['status'],'3')
        self.assertEqual(re['start'],[10,11])
        self.assertEqual(re['nexttest'],'8')
        self.assertEqual(str(re['testcmd']),'a 1,b 3,c 4')
        re = ss.check_board_status('10.0.10.28')
        self.assertTrue(isinstance(re,dict))
        self.assertEqual(re['ip'],'10.0.10.28')
        self.assertEqual(re['status'],'0')
        self.assertTrue(isinstance(re['start'],list))
        self.assertEqual(re['nexttest'],'-')
        self.assertEqual(re['testcmd'],'-')

    def test_get_status(self):
        ss = TCPServerSocket('../config_server.ini')
        create_table(self.db_name)
        re = ss.get_status('10.0.10.27')
        self.assertEqual(re['status'],'3')
        self.assertEqual(re['start'],[10,11])
        self.assertEqual(re['tested'],'hotplug')
        self.assertEqual(re['nexttest'],'8')
        self.assertEqual(re['testcmd'],'a 1,b 3,c 4')

    def test_update_status(self):
        create_table(self.db_name)
        ss = TCPServerSocket('../config_server.ini')
        ss.update_status('10.0.10.27',status = '3')
        conn = sqlite3.connect(self.db_name)
        cursor = conn.execute('''select status from %s where id = 1;'''%self.board_name)
        for c in cursor:
            self.assertEqual(c[0],'3')
        conn.close()

    def test_handle_result(self):
        create_table(self.db_name)
        os.mkdir('log_dir')
        f = open('log_dir/10.0.10.27hotplug.log','w')
        f.write('This is a unit test!')
        f.close()
        ss = TCPServerSocket('../config_server.ini')
        conn = sqlite3.connect(self.db_name)
        recv_data = {'ip':'10.0.10.27','result':'pass'}
        ss.handle_result(recv_data)
        recv_data = {'ip':'10.0.10.27','result':'fail'}
        ss.handle_result(recv_data)
        pass_name = 'function_pass_0x0a000a1b_hotplug.log'
        fail_name = 'function_fail_0x0a000a1b_hotplug.log'
        year = datetime.now().year
        month = datetime.now().month
        if month < 10:
            month = '0' + str(month)
        day = datetime.now().day
        if day < 10:
            day = '0' + str(day)
        ftp = FTP('172.29.40.183')
        ftp.login('rspcmantis','_Rspcmantis121')
        dirname = '/home/rspcmantis/Desktop/web/data/'
        remotedir = dirname + str(year) +str(month) + str(day)
        ftp.cwd(remotedir)
        self.assertTrue(pass_name in ftp.nlst())
        self.assertTrue(fail_name in ftp.nlst())
        ftp.quit()


    def tearDown(self):
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        if os.path.exists('log_dir'):
            shutil.rmtree('log_dir')
        pass

class BoardLibUnitTest(unittest.TestCase):
    def setUp(self):
        self.ip = '10.0.10.27'

    def test_check_board_on_line(self):
        self.assertEqual(0, check_board_on_line(self.ip))

    def test_get_board_info(self):
        ins = get_board_info(self.ip)
        self.assertTrue(isinstance(ins, dict))
        self.assertTrue(ins['status'] == 'succeed')

    def tearDown(self):
        pass

class FWTestLibUnitTest(unittest.TestCase):
    def setUp(self):
        self.ip = '10.0.10.27'
        if os.path.exists('fwtest_lib.db'):
            os.remove('fwtest_lib.db')
        conn = sqlite3.connect('fwtest_lib.db')
        conn.execute('''CREATE TABLE fwtest
                    (id integer primary key autoincrement,
                     ip           text,
                     status       text,
                     sensor       text);''')
        conn.execute("INSERT INTO fwtest (id,ip,status,sensor) VALUES (1,'10.0.10.27','1','ov9715');")
        conn.commit()
        conn.close()

    def _test_get_board_info(self):
        status_param = ('sdkVersion', 'macAddr', 'protocol', 'encryption', 'bssid',
                'state', 'dns1', 'buildTime', 'ipAddr', 'upTime', 'fwVersion',
                'subnetMask', 'gateway', 'uuid')
        re = util.fwtest_lib.get_board_info(self.ip)
        self.assertTrue(isinstance(re, dict))
        self.assertTrue(len(re) != 0)
        for param in status_param:
            self.assertTrue(re.has_key(param),'dict has no key:%s'%param)

    def test_get_board_info(self):
        status_param = ('sdkVersion', 'macaddr', 'essid',
                'state', 'dns1', 'buildTime', 'ipaddr', 'upTime', 'fwVersion',
                'netmask', 'gateway', 'uuid')
        re = util.fwtest_lib.get_board_info(self.ip)
        self.assertTrue(isinstance(re, dict))
        self.assertTrue(len(re) != 0)
        re_dict = {}
        re_dict.update(re['staInfo'])
        re_dict.update(re['sysInfo'])
        re_dict.update(re['wanInfo'])
        for param in status_param:
            self.assertTrue(re_dict.has_key(param),'dict has no key:%s'%param)

    def test_set_fwtest_status(self):
        lock = multiprocessing.Lock()
        util.fwtest_lib.set_fwtest_status(lock, 'fwtest_lib.db', 'fwtest', 1, '5')
        status = db.find('fwtest_lib.db', 'fwtest', 1, 'status')
        self.assertEqual(status, '5')

    def test_get_fwtest_status(self):
        lock = multiprocessing.Lock()
        status = util.fwtest_lib.get_fwtest_status(lock, 'fwtest_lib.db', 'fwtest', 1, 'status')
        self.assertEqual(status, '1')

    def test_list_online_board(self):
        util.fwtest_lib.list_online_board('10.0.10.1', '10.0.0.20')
        util.fwtest_lib.list_online_board('10.0.10.20', '10.0.0.1')
        util.fwtest_lib.list_online_board('10.0.10.27', '10.0.0.27')

    def test_check_board_status(self):
        re =util.fwtest_lib.check_board_status('fwtest_lib.db', 'fwtest', '10.0.10.27')
        self.assertEqual(re, '1')
        re =util.fwtest_lib.check_board_status('fwtest_lib.db', 'fwtest', '10.0.10.28')
        self.assertEqual(re, None)

    def test_get_ip_from_sensor(self):
        re = util.fwtest_lib.get_ip_from_sensor('fwtest_lib.db', 'fwtest', 'ov9715')
        self.assertEqual(re, '10.0.10.27')
        re = util.fwtest_lib.get_ip_from_sensor('fwtest_lib.db', 'fwtest', 'ov9716')
        self.assertEqual(re, None)

    def tearDown(self):
        os.remove('fwtest_lib.db')

class CommonLibUnitTest(unittest.TestCase):
    def setUp(self):
        self.config_name = 'config_unittest.ini'
        self.proj_sec = '[info]\n'
        self.content = 'ip = 10.0.0.1'
        with open(self.config_name, 'w') as fd:
            fd.write(self.proj_sec)
            fd.write(self.content)

    def test_get_routine_test_ip_list(self):
        re = get_routine_test_ip_list(self.config_name, self.proj_sec[1:-2])
        self.assertTrue(re == '10.0.0.1')

    def test_get_cmd_list(self):
        re = get_cmd_list(self.config_name, self.proj_sec[1:-2], 'ip')
        self.assertTrue(re == '10.0.0.1')

    def test_get_download_file_info(self):
        re = get_download_file_info(self.config_name, self.proj_sec[1:-2])
        self.assertTrue(re['ip'] == '10.0.0.1')

    def test_get_start_test_time(self):
        with open(self.config_name, 'w') as fd:
            fd.write('\n')
            fd.write('[start_time]')
            fd.write('\n')
            fd.write('start_hour = 10')
            fd.write('\n')
            fd.write('start_minute = 20')
            fd.write('\n')
        re = get_start_test_time(self.config_name, 'start_time')
        self.assertTrue(isinstance(re,tuple))
        self.assertTrue(len(re) == 2)
        self.assertTrue(re[0] == 10, re[1] == 20)

    def test_get_update_kernel_time(self):
        re = get_update_kernel_time('../config_server.ini', 'update_kernel')
        self.assertTrue(isinstance(re, tuple))
        self.assertTrue(re[0] >= 0 and re[0] < 24)
        self.assertTrue(re[1] >= 0 and re[1] < 60)

    def tearDown(self):
        os.remove(self.config_name)

class SocketUnitTest(unittest.TestCase):
    def setUp(self):
        self.db_name = 'ipcamtest.db'
        self.ss = TCPServerSocket('../config_server.ini')
        create_table(self.db_name)

    def test_geid_byip(self):
        i = self.ss.getid_byip(self.db_name, 'board', '10.0.10.27')
        self.assertEqual(i, 1)

    def test_add_boardinfo2db(self):
        test_list = 'a:1,b:2,c:3'
        self.ss.add_boardinfo2db('10.0.10.27', test_list)
        status = db.find('ipcamtest.db', 'board', 1, 'status')
        tested = db.find('ipcamtest.db', 'board', 1, 'tested')
        testlist = db.find('ipcamtest.db', 'board', 1, 'testlist')
        extra_ftp_server = db.find('ipcamtest.db', 'board', 1, 'extra_ftp_server')
        extra_flag = db.find('ipcamtest.db', 'board', 1, 'extra_flag')
        self.assertEqual(status, '0')
        self.assertEqual(tested, '-')
        self.assertEqual(testlist, 'a:1,b:2,c:3')
        self.assertEqual(extra_ftp_server, '-')
        self.assertEqual(extra_flag, '-')

    def test_run_init(self):
        self.ss.run_init('10.0.10.27')
        nexttest = db.find('ipcamtest.db', 'board', 1, 'nexttest')
        testcmd = db.find('ipcamtest.db', 'board', 1, 'testcmd')
        self.assertEqual(nexttest, 'hotplug_test')
        self.assertEqual(testcmd, 'hotplug.sh')

    def test_handle_attribute(self):
        data = {'set_time':[10,20]}
        command_name = 0
        self.ss.handle_attribute(data,command_name)
        start_time = db.find('ipcamtest.db', 'board', 1, 'start')
        self.assertEqual(start_time, '(10, 20)')
        data = {'get_time':[]}
        re = self.ss.handle_attribute(data,command_name)

    def test_check_webdata(self):
        data1 = {'set_time':'','get_time':''}
        data2 = {'get_time':''}
        data3 = {'set_time':''}
        data4 = {'set1_time':''}
        self.assertTrue(self.ss.check_webdata(data1))
        self.assertTrue(self.ss.check_webdata(data2))
        self.assertTrue(self.ss.check_webdata(data3))
        self.assertFalse(self.ss.check_webdata(data4))

    def test_init_fw_table(self):
        db_name = 'ipcamtest.db'
        table_name = 'fwboard'
        create_fw_table(db_name)
        self.ss.init_fw_table()
        ip1 = db.find(db_name, table_name, 1, 'ip')
        sensor1 = db.find(db_name, table_name, 1, 'sensor')
        ip2 = db.find(db_name, table_name, 2, 'ip')
        sensor2 = db.find(db_name, table_name, 2, 'sensor')
        if ip1 == '10.0.10.74':
            self.assertEqual(sensor1, 'ov9715')
            self.assertEqual(sensor2, 'ov9750')
            self.assertEqual(ip2, '10.0.10.75')
        elif ip1 == '10.0.10.75':
            self.assertEqual(sensor1, 'ov9750')
            self.assertEqual(sensor2, 'ov9715')
            self.assertEqual(ip2, '10.0.10.74')

        else:
            self.assertTrue(False)

    def test_send_result_to_web(self):
        db_name = 'ipcamtest.db'
        table_name = 'fwboard'
        ip = '10.0.10.74'
        create_fw_table(db_name)
        db.insert_info(db_name, table_name, ip)
        ide = self.ss.getid_byip(db_name, table_name, ip)
        db.update(db_name, table_name, ide, sensor = 'ov9715')
        self.ss.send_result_to_web('10.0.10.74', sys.argv[0])
        status = db.find(db_name, table_name, 1, 'status')
        self.assertEqual(status, '0')

    def tearDown(self):
        os.remove(self.db_name)
        del self.ss

if __name__ == '__main__':
    #suite = unittest.TestSuite()
    #suite.addTest(IPCUnitTest('test_handle_result'))
    suite1 = unittest.TestLoader().loadTestsFromTestCase(BoardLibUnitTest)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(DBUnitTest)
    suite3 = unittest.TestLoader().loadTestsFromTestCase(FWTestLibUnitTest)
    suite4 = unittest.TestLoader().loadTestsFromTestCase(CommonLibUnitTest)
    suite5 = unittest.TestLoader().loadTestsFromTestCase(SocketUnitTest)
    unittest.TextTestRunner().run(suite1)
    unittest.TextTestRunner().run(suite2)
    unittest.TextTestRunner().run(suite3)
    unittest.TextTestRunner().run(suite4)
    unittest.TextTestRunner().run(suite5)
    #unittest.main()
