
#!/usr/bin/python

import os
import sys
import re
import pexpect
import time

def process_uboot():
	foo = pexpect.spawn('minicom')
	foo.sendline('\n')
	foo.expect('~ #')
	foo.sendline('reboot')
	foo.expect('Hit any key to stop autoboot:')
	foo.sendline('\n')
	foo.sendline('update all \n')

def prepare_tftp_server():
	tftp = pexpect.spawn('tftp 10.0.10.40')
	tftp.expect('tftp>')
	tftp.send('binary\n')
	tftp.expect('tftp>')
	tftp.send('put linux.bin\n')
	time.sleep(20)

def process_run():
	foo = pexpect.spawn('minicom')
	foo.sendline('\n')
	foo.expect('rlxboot#')
	foo.sendline('reset\n')

if __name__ == '__main__':
	process_uboot()
	prepare_tftp_server()
	time.sleep(40)
	process_run()
	time.sleep(5)

