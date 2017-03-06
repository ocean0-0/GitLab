#!/usr/bin/python
# -*- coding:utf-8 -*-

import smtplib
import os
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders


def mail(receiver, subject, content, attach_dir, attach_name):
    
	mail_host = 'mail.realsil.com.cn:25' 
	mail_user = 'linda_bao'
	mail_psd = 'rs518310!'
	mail_sender = 'linda_bao@realsil.com.cn'
    
	msg = MIMEMultipart()
	body = MIMEText(content, _subtype='html', _charset='utf-8')
    
	msg.attach(body)
	msg['Subject'] = subject
	msg['From'] = mail_sender
    
	part = MIMEBase('application', 'octet-stream')
	part.set_payload(open(attach_dir, 'rb').read())
	Encoders.encode_base64(part)

	part.add_header('Content-Disposition', 'attachment; filename='+attach_name)
	msg.attach(part)

	try:
		s = smtplib.SMTP()
		s.connect(mail_host)
		s.login(mail_user, mail_psd)
		s.sendmail(mail_sender, receiver,msg.as_string())
		s.close()
		print 'send mail sucess'
		return True
	except Exception, e:
		print str(e)
		return False


def mail_mutt(receiver, subject, content,attach_dir, attach_name):
	cmd = 'echo '+'\"'+ content +'\"'+' '+ '| ' + 'mutt ' +receiver \
			+ ' -s '+ '\"' +subject + '\"'+ ' -a ' + attach_dir
	os.system(cmd)


if __name__ == '__main__':
	
	mail('linda_bao@realsil.com.cn', 'test mail lalal', 'here', '/home/linda/Desktop/fw.log', 'fw.log')
