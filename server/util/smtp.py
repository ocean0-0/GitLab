
#!/usr/bin/python
#coding: UTF-8
import os
import sys
import base64
import socket
import smtplib
import ConfigParser
import util
from httplib2 import socks
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendMail(object):
    """docstring for SendMail"""
    _CONFIGINI = '../config.ini'

    def get_mails(self,proj_name):
        config = ConfigParser.ConfigParser()
        config.read(self._CONFIGINI)
        if config.has_section(proj_name):
            options = config.options(proj_name)
            for key in options:
                if key == 'mail':
                    return config.get(proj_name,key)
        return ''

    def do_mail(self,mail,test_name,log_name = '',content = ''):
        socket.socket = socks.socksocket
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1", 7070)
        msg = MIMEMultipart()
        att1 = MIMEText(open(log_name, 'rb').read(), 'base64', 'gb2312')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename=' + log_name
        msg.attach(att1)
        message = content
        body = MIMEText(message,_subtype = "plain")
        msg.attach(body)
        msg['to'] = mail
        msg['from'] = 'shanjian_fei@realsil.com.cn'
        msg['subject'] = test_name
        try:
            server = smtplib.SMTP('mail.realsil.com.cn:465')
            server.login('shanjian_fei@realsil.com.cn','Rt478!')
            server.sendmail(msg['from'], msg['to'],msg.as_string())
            server.quit()
            print 'send success'
        except Exception, e:
            print "fail\n"
            print str(e)
if __name__ == '__main__':
    test = SendMail()
    content = ''
    info = util.get_dict_from_config('../config.ini','ftp_server')
    content = info['urlweb']
    content = 'please visit: ' + content
    mail = test.get_mails('check_compile')
    test.do_mail(mail,'check_compile','smtp.py',content)
