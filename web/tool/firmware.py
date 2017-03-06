# !/usr/bin/python 
# -*- coding:utf-8 -*-
# author:linda_bao

import glob
import json
import os
import re
import smtplib 
import socket
import sys
import time
from email.mime.text import MIMEText 

import mail
import packet


def file_write(w_file ,content):
	
	# if not os.path.exists(w_file):
	# 	os.mkdir(w_file)		

	try:
		with open(w_file, 'w') as f:
			f.write(content)
	except:
			print 'Error occurs while writting file.'



def file_read(r_file):

	line = ''
	content = ''

	try:
		with open(r_file, 'r') as f:
			for line in f:
				content += '<p><a>' + line + '</a></p>'
			print content
	except:
		content = 'Error occurs while reading file.'
	
	finally:
		print content

	return content


'''
   function: find data/firmware*.log
   para    : file_dir='data/',
   			 option='firmware*.log'
   			 file_list=['data/firmware_ov9715.log','data/firmware_ov9715.log',...]
   return  : file_name = 'firmware_ov9715.log'
'''
def file_search(file_dir, option):
	
	file_path = ''
	file_name = ''
	file_list = ''
	result = ''
	folder = time.strftime('%Y%m%d')
	
	file_list = glob.glob(file_dir + option)
	
	# create a new folder
	des_path = file_dir + folder
	if not os.path.exists(des_path):
		os.system('mkdir '+ des_path)
		print folder

	for file_path in file_list:
		
		tag_index = file_path.index('firmware')
		file_name = file_path[tag_index:]
		file_head_length = len('firmware_pass_')
		folder = file_path[file_head_length+5:file_head_length+13]
		print 'folder:%s' % folder

		# create a new folder
		des_path = file_dir + folder
		if not os.path.exists(des_path):
			os.system('mkdir '+ des_path)

		cmd_mv = 'mv ' + file_path +' '+ des_path
		os.system(cmd_mv)
		result = file_name

	return result


'''
	function      : Send request to server(172.29.43.31)
	function calls: packet.pack_data()
				    packet.unpack_data()
	command format: {"command":"get_status"，“sensor”：“ov9715”} 
	receive date  : {"data": 0}
	data status   : 0-free 
					1-upload finished
					2-update image finished
					3-test finished
'''
def send_request(s_ip, s_port, cmd):

	buf = ''
	buf_unpack = ''
	cmd_packet = ''
	status = ''

	# server info 
	HOST = s_ip
	PORT = s_port

	# pack cmd to the require format for send
	cmd_packet = packet.pack_data(0.1, 0x00030001, cmd)

	# make connect to the server
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, e:
		print "Error occurs while creating socket: %s" % e
		s.close()

	try:
		s.connect((HOST, PORT))
	except socket.gaierror, e:
		print "Address-related error occurs while connecting to server: %s" % e
		s.close()
	except socket.error, e:
		print "Connection error: %s" % e

	# send the request to the server
	try:
		s.sendall(cmd_packet)
	except socket.error, e:
		print "Error occurs while sending data: %s" % e
		s.close()


	# obtain the response from the server 
	try:
		# set connect timeout <=5s
		s.settimeout(5)
		buf = s.recv(1024)
		if len(buf) != 0:
			buf_unpack = packet.unpack_data(buf)
			status = buf_unpack[2]['status']['data']
	except socket.timeout:
		print "Connect time out."
		s.close()
	except socket.error, e:
		print "Error occurs while receiving data: %s" % e

	s.close()

	return status


'''
	get firmware board list
	board_list = {u'ov9750': u'10.0.2.97', u'ov9715': u'10.0.10.25'}
'''
def get_firmware_board_list(s_ip, s_port):

	try:
		cmd = {'command':'get_table_fwtest','sensor':'ov9715'}
		board_list = send_request(s_ip, s_port, cmd)

		return board_list
		
	except e:
		print "Error occurs while getting firmware board list:%s" % e


'''
	get firmware status
'''
def get_firmware_board_status(sensor,s_ip, s_port):

	try:
		cmd = {'command':'get_status','sensor':sensor}
		status = send_request(s_ip, s_port, cmd)
		return status
	except e:
		print "Error occurs while getting firmware board status:%s" % e


'''
	check firmware online or not
'''
def check_firmware_board_online(sensor,s_ip, s_port):
	
	try:
		cmd = {'command':'check_online','sensor':sensor}
		status_online = send_request(s_ip, s_port, cmd)
		return status_online
	except e:
		print "Error occurs while checking firmware board online:%s" % e



'''
	get avilable board list for firmware test 
'''
def get_firwmare_board_list(s_ip, s_port):
	
	try:
		cmd = {'command':'get_table_fwtest','sensor':'ov9715'}
		board_list = send_request(s_ip, s_port, cmd)
		return board_list
	except e:
		print "Error occurs while getting firmware board list:%s" % e



def main():
    
    # server   
	server_ip = '172.29.43.31'
	server_port = 20000
	sensor = 'ov9715'
	cmd = {"command":"get_status","sensor":"ov9715"}
	
	send_request(server_ip, server_port, cmd)

	# file test
	file_path = 'firmware_pass_20161225.log'
	content = 'This is file_test.'
	# file_write(file_path, content)
	# file_read(file_path)
	# file_search('./', 'firmware*.log')
	# print 'get firmware board status'
	# print get_firmware_board_status(sensor,server_ip, server_port)
	print 'check firmware board online'
	print check_firmware_board_online(sensor,server_ip, server_port)
	print 'get firmware board list'
	board_list = get_firwmare_board_list(server_ip, server_port)
	# get the sensor type list
	sensor_list = map(str, board_list.keys())
	# get the board ip list
	ip_list = map(str, board_list.values())
	print board_list
	print sensor_list
	print ip_list
	


if __name__ == '__main__':

	main()
    
