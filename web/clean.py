#!/usr/bin/env python

import os

def clean_pyc(path):
    dirs = os.listdir(path)
    for d in dirs:
        filepath = os.path.join(path,d)
        if os.path.isdir(filepath):
            clean_pyc(filepath)
        else:
            if 'pyc' in d:
                os.remove(filepath)
if __name__ == '__main__':
    clean_pyc('.')
