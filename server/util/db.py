#! /usr/bin/python2.7
#coding:UTF-8
#date               :2016.08.02

import os
import sqlite3


# create table if not exists
def create_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''create table if not exists %s(
                id integer primary key autoincrement,
                ip                  text,
                status              text,
                cgi_status          text,
                testlist            text,
                tested              text,
                nexttest            text,
                testcmd             text,
                ftp_server          text,
                start               text,
                extra_flag          text,
                extra_tested        text,
                extra_testlist      text,
                extra_nexttest      text,
                extra_testcmd       text,
                extra_ftp_server    text);'''%table_name)
    conn.close()


#create fw table in db
def create_fw_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''create table if not exists %s(
                id integer primary key autoincrement,
                ip                  text,
                sensor              text,
                status              text);'''%table_name)
    conn.close()


#remove table
def remove_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''drop table %s;'''%table_name)
    conn.close()


def check_table_name(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type = 'table';''')
    re = cursor.fetchall()
    conn.close()
    for i in re:
        if table_name in i:
            return True
    return False


def remove_db(db_name):
    os.remove(db_name)


def insert_info(db_name, table_name, ip):
    conn = sqlite3.connect(db_name)
    conn.execute('''insert into %s(%s) values('%s');'''%(table_name,'ip',ip))
    conn.commit()
    conn.close()


def del_from(db_name, table_name, identify):
    conn = sqlite3.connect(db_name)
    conn.execute('''delete from  %s where id = %s;'''%(table_name,identify))
    conn.commit()
    conn.close()

def update(db_name, table_name, identify, **args):
    keys = args.keys()
    conn = sqlite3.connect(db_name)
    value = args[keys[0]]
    for k in keys:
        conn.execute('''update %s set %s = '%s' where id = %s;'''%(table_name,k,args[k],identify))
    conn.commit()
    conn.close()

def find(db_name, table_name, identify, *args):
    re = {}
    conn = sqlite3.connect(db_name)
    for k in args:
        cursor = conn.execute('''select %s from %s where id = %s;'''%(k,table_name,identify))
        for c in cursor:
            re[k] = c[0]
            break
    return re

def add_column(db_name, table_name, column):
    conn = sqlite3.connect(db_name)
    conn.execute('''alter table %s add column %s text;'''%(table_name,column))
    conn.commit()
    conn.close()

def get_allcolumn(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("select * from %s;"%table_name)
    col_name_list = [tuple[0] for tuple in cursor.description]
    return col_name_list

def get_allid(db_name, table_name):
    idy = []
    conn = sqlite3.connect(db_name)
    cursor = conn.execute('''select id from %s;'''%table_name)
    for c in cursor:
        idy.append(c[0])
    return idy

def get_id(db_name, table_name, ip_client):
    for i in get_allid(db_name, table_name):
        if find(db_name, table_name, i, 'ip')['ip'] == ip_client:
            return i
    return None

if __name__ == '__main__':
    #print get_allid('ipcamtest.db','board')
    print get_id('../ipcamtest.db','fwboard','10.0.10.27')
    #data = ['ip','status']
    #data = ['ip']
    #print find('ipcamtest.db','board',1,'ip','status')
    #print get_allid('test.db','ipcam')
    #re = get_allcolumn('ipcamtest.db','board')
    #print re
