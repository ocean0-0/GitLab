
#!/usr/bin/python

import os
import re
import socket
import time
import packet
import json
import sys

VERSION_LEN = 8
PACKET_LEN = 4
COMMAND_LEN = 4
CHECKSUM_LEN = 1

PACKET_LEAST_LEN = VERSION_LEN + \
			PACKET_LEN + \
			COMMAND_LEN + \
			CHECKSUM_LEN
'''
  param1: ip   = 10.0.1.11
  param2: port = 20000
  param3: hour = 8
  param4: min  = 30
'''

def retrieve_file(ip, port):

	except_flag = 0

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	s.settimeout(20)

	time.sleep(2)

	try:
		s.sendall(packet.pack_data(0, 0x10000, {'retrieve_file': []}))
	except:
		s.close()
		return

	'''sleep for a second'''
	time.sleep(1)

	data = ''
	while True:
		try:
			buf = s.recv(1024)
		except:
			except_flag = 1

		if not buf or except_flag == 1:
			s.close()
			return

		data += buf
		if len(data) < PACKET_LEAST_LEN:
			continue

		num0 = ord(data[8])
		num1 = ord(data[9])
		num2 = ord(data[10])
		num3 = ord(data[11])
		num = (num0 << 24) | (num1 << 16) | (num2 << 8) | num3

		if len(data) == (PACKET_LEAST_LEN + num):
			break

	version, command_id, js = packet.unpack_data(data)
	s.close()

	return js['result']


def main():

	print retrieve_file(sys.argv[1], int(sys.argv[2]))

	
if __name__ == '__main__':
	main()


