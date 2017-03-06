import os
import time

from socket import *
from pack import PackData

ADDR = ('',30000)
s = socket(AF_INET, SOCK_STREAM)
s.bind(ADDR)
s.listen(1)
client,addr = s.accept()
data = client.recv(1024)
print data
