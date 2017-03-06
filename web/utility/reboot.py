
#!/usr/bin/python

import pexpect
import time

def process_reboot():
	foo = pexpect.spawn('minicom')
	foo.sendline('\n')
	foo.expect('~ #')
	foo.sendline('reboot\n')

if __name__ == '__main__':
	cnt = 0
	while True:
		print cnt
		cnt += 1
		process_reboot()
		time.sleep(60)

