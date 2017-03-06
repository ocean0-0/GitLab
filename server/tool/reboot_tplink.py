
#!/usr/bin/python

import re
import os
import pexpect
import time

def read_log():

    f = open('log.txt','r')
    pos = 0
    for line in range(20):
        while True:
            pos = pos - 1
            try:
                f.seek(pos, os.SEEK_END)
                if f.read(1) == '\n':
                    break
            except Exception,e:
                print e
                f.seek(0,0)
        line = f.readline().strip()
        if re.findall('No such file or directory',line):
            print line
            f.close()
            return -1
            break
    f.close()


def tp_reboot():
    fout = open ('log.txt', "w")
    foo = pexpect.spawn('minicom',logfile = fout)
    time.sleep(10)
    foo.sendline('\n')
    time.sleep(10)
    foo.expect('SLP login:')
    foo.send('root\n')
    foo.expect('Password:')
    foo.send('slphisillicon\n')
    foo.expect('root@SLP:~#')

    time.sleep(1)
    foo.send('ls /dev/video51\n')
    time.sleep(1)
    foo.send('ls /dev/video52\n')
    time.sleep(1)
    foo.send('ls /dev/video53\n')
    time.sleep(1)
    foo.send('ls -l\n')
    foo.expect('root@SLP:~#')
    foo.sendline('reboot\n')
    time.sleep(1)
    fout.close()

if __name__ == '__main__':
    cnt = 0
    while True:
        os.system('rm log.txt')
        print cnt
        cnt += 1
        tp_reboot()
        if read_log() == -1:
            break
        time.sleep(60)

