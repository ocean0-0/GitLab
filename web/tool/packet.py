
#!/usr/bin/python

import os
import sys
import re
import struct
import json

def get_version(version):

	version_str = str(version)
	length = len(version_str)
	if length > 8:
		version_str = ''
	elif length < 8:
		for i in range(8 - len(version_str)):
			version_str += ' '
	return version_str

def get_checksum(data, num):

	val = ord(data[0])
	for i in range(num-1):
		val ^= ord(data[i+1])

	return val

def pack_data(version, command_id, json_data):

	version_str = get_version(version)
	js = json.dumps(json_data)
	length = len(js)
	check = get_checksum(js, length)

	''' ! means net order'''
	return struct.pack('!8sii' + str(length) + 'sc', version_str, length, command_id, js, chr(check))

def unpack_data(data):

	num0 = ord(data[8])
	num1 = ord(data[9])
	num2 = ord(data[10])
	num3 = ord(data[11])
	length = (num0 << 24) | (num1 << 16) | (num2 << 8) | num3

	'''! means net order'''
	version_str, var, command_id, js, check = struct.unpack('!8sii' + str(length) + 'sc', data)
	checksum = get_checksum(js, len(js))
	if checksum <> ord(check):
		assert 0
	
	return float(data[0:7]), command_id, json.loads(js)

def main():

	print 'hello, world'
	print len(get_version(1.1))
	print get_checksum('123', 3)
	print unpack_data(pack_data(1.1, 1, {'1':2}))

if __name__ == '__main__':

	main()



