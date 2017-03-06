
#!/usr/bin/python

import os
import re
import socket
import time
import packet
import json

VERSION_LEN = 8
PACKET_LEN = 4
COMMAND_LEN = 4
CHECKSUM_LEN = 1

PACKET_LEAST_LEN = VERSION_LEN + \
			PACKET_LEN + \
			COMMAND_LEN + \
			CHECKSUM_LEN

def get_data():

	for i in range(100):

		except_flag = 0

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('localhost', 8001))
		time.sleep(2)

		try:
			s.sendall(packet.pack_data(0.1, 1, {'id':1}))
		except:
			s.close()
			continue

		'''sleep for a second'''
		time.sleep(1)

		data = ''
		while True:
			try:
				buf = s.recv(1024)
			except:
				except_flag = 1

			if not buf or except_flag == 1:
				break

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

		if not buf or except_flag == 1:
			s.close()
			continue

		version, command_id, js = packet.unpack_data(data)
		print type(version)
		print type(command_id)
		print type(js)

		s.close()

def main():

	get_data()
	

if __name__ == '__main__':
	main()


