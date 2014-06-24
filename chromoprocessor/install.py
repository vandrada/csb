#!/usr/bin/env python

import sys
import urllib
import os
import tarfile
import subprocess
from os.path import expanduser

argparse =\
    "http://pypi.python.org/packages/source/a/argparse/argparse-1.2.1.tar.gz"

home = expanduser('~')
os.chdir(home)

def dir_name(url):
    """
    gets the would-be directory name from a pypi url
    """
    return '.'.join(url.split('/')[-1].split('.')[:-2])

try:
    import blah
except ImportError:
    argparse_dir = dir_name(argparse)
    print "installing argparse to ~/%s" % (argparse_dir)
    urllib.urlretrieve(argparse, filename="argparse.tar.gz")
    # extract
    argparse_tar = tarfile.open("argparse.tar.gz")
    argparse_tar.extractall()
    argparse_tar.close()
    os.remove(argparse_tar.name)
    # install
    os.chdir(argparse_dir)
    subprocess.call(['python', 'setup.py', 'install', '--user'])

try:
    import concurrent.futures
except ImportError:
    print "installing concurrent"
    # install concurrent
