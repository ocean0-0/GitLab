
#!/usr/bin/python

import os
import sys
import re
import socket
import packet

VERSION_LEN = 8
PACKET_LEN = 4
COMMAND_LEN = 4
CHECKSUM_LEN = 1

PACKET_LEAST_LEN = VERSION_LEN + \
			PACKET_LEN + \
			COMMAND_LEN + \
			CHECKSUM_LEN

total_num = 0


def process_packet(s, pkt):
	
	global total_num
	total_num += 1

	version, command_id, js = packet.unpack_data(pkt)
	print total_num

	buf = packet.pack_data(0.1, 0, {'result':'ok'})
        

	try:
		while buf:
			num = s.send(buf)
			buf = buf[num:]	
	except:
		buf = ''
		return 1

	return 0


def run():

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('localhost', 8001))
	sock.listen(5)

	while True:

		data = ''
		s, addr = sock.accept()

		while True:

			try:
				except_flag = 0
				buf = s.recv(1024)
			except:
				except_flag = 1

			if not buf or except_flag == 1:
				break

			data += buf
			if len(data) >= PACKET_LEAST_LEN:

				num0 = ord(data[8]) 
				num1 = ord(data[9]) 
				num2 = ord(data[10]) 
				num3 = ord(data[11])
				num = (num0 << 24) | (num1 << 16) | (num2 << 8) | num3

				if (len(data) - PACKET_LEAST_LEN) >= num:

					pkt = data[0: num + PACKET_LEAST_LEN]
					data = data[num + PACKET_LEAST_LEN:]
 
					result = process_packet(s, pkt)
					if result != 0:
						break
		s.close()

def main():

	run()

if __name__ == '__main__':

	main()


