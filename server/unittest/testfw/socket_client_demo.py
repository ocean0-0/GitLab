#--*-- coding:utf-8 --*--
import os
import time

from socket import *
from pack import PackData

ADDR = ('172.29.43.31',30000)

dir_path = os.getcwd()
#data = {'file_path':[os.getcwd() + '/hotplug.sh',os.getcwd() + '/config.ini']}
#data = {'get_status':0}

data = {'ip':'172.29.40.183','port':'30000','usr':'rspcmantis','psd':'_Rspcmantis121','sdk_version':'sdk-v1.0.3','sensor':'ov9715','dir_path':dir_path,'file_list':['ov9715.bin','ov9750.bin'],'filename_fw':'ov9715.bin'}

s = socket(AF_INET,SOCK_STREAM)
s.connect(ADDR)

pd = PackData()
body = pd.pack_data('0.1',0x00030001,data)
s.sendall(body)

data = s.recv(1024)
print data
s.close()
