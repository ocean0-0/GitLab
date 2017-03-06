#!/usr/bin/python
# -*-coding: UTF-8-*-
# Realsil
# Author : Shanjian Fei
# Mail : <shanjian_fei@realsil.com.cn>
# Date : 2016.11.7

import struct
import sys
import json

class PackData(object):

    version = ''
    length = 0
    command = 0
    body = {}
    checksum = 0

    BUFFER_SIZE = 1024
    VERSION_SIZE = 8
    LENGTH = 4
    COMMAND_SIZE = 4
    CHECKSUM_SIZE = 1

    def set_version(self,version):

        version = str(version)
        version_size = len(version)
        if version_size <= self.VERSION_SIZE:
            for i in range(self.VERSION_SIZE-version_size):
                version = version + ' '
        else:
            version = '        '
            print 'version less than 9'
            print "The version was set None "
        self.version = version


    def get_version(self,recv_data):

        data = self.unpack_data(recv_data)
        data_version = data[0]
        return data_version.split('*')[0]


    def get_body_len(self,recv_data):

        recv_data8 = ord(recv_data[8])
        recv_data9 = ord(recv_data[9])
        recv_data10 = ord(recv_data[10])
        recv_data11 = ord(recv_data[11])
        return (recv_data8 << 24) | (recv_data9 << 16) | \
        (recv_data10 << 8) | (recv_data11)


    def get_command_id(self,recv_data):

        data = self.unpack_data(recv_data)
        command = data[2]
        return command


    def get_command(self,recv_data):

        device_type = ord(recv_data[12])
        test_type = ord(recv_data[13])
        test_name1 = ord(recv_data[14])
        test_name2 = ord(recv_data[15])
        return device_type,test_type,(test_name1 << 8) | test_name2


    def get_body(self,recv_data):

        data = self.unpack_data(recv_data)
        body = data[3]
        body = json.loads(body)
        return body


    def create_checksum(self,body):

        check_num = 0
        body = json.dumps(body)
        for i in range(len(body)):
            if i == 0:
                check_num = ord(body[0])

            else:
                check_num = check_num ^ ord(body[i])

        return chr(check_num)


    def get_checksum_from_recvdata(self,recv_data):

        data = self.unpack_data(recv_data)
        check_num = data[4]
        return check_num


    def check_data(self,recv_data):

        packet_len = self.VERSION_SIZE + self.COMMAND_SIZE + \
        self.get_body_len(recv_data) + self.CHECKSUM_SIZE + self.LENGTH
        if len(recv_data) == packet_len:
            #check checksum
            if self.create_checksum(self.get_body(recv_data)) == self.get_checksum_from_recvdata(recv_data):
                return True
            else:
                return False
        else:
            print 'data error! please send again!'
            return False


    def pack_data(self,version,command_id,body):

        self.set_version(version) #8
        version = self.version

        body = json.dumps(body)

        length = len(body)
        checksum = self.create_checksum(body)

        fmt = '!' + str(self.VERSION_SIZE) + 'siI' + str(length) + 'sc'
        message_packet = struct.pack(fmt,version,length,command_id,body,checksum)
        return message_packet


    def unpack_data(self,packet_data):
        length = self.get_body_len(packet_data)
        fmt = '!' + str(self.VERSION_SIZE) + 'siI' + str(length) + 'sc'
        return struct.unpack(fmt,packet_data)


    def get_real_data(self,data):
        return data.split('*')[0]


if __name__ == '__main__':

    test = PackData()
    command = 0x01000011
    data = {'command233455':100,'timeout':101}
    data1 = test.pack_data('10.0.1',command,data)
    print test.unpack_data(data1)

