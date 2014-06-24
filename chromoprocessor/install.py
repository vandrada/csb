#!/usr/bin/env python

"""
Installs the dependencies of chromoprocessor
"""

import sys
import urllib
import os
import tarfile
import shutil
import subprocess

def dir_name(url):
    """
    gets the would-be directory name from a pypi url
    """
    return '.'.join(url.split('/')[-1].split('.')[:-2])

def install(lib, url):
    os.chdir(HOME)
    lib_dir = dir_name(lib)
    print "installing %s to ~/%s" (lib, lib_dir)
    urllib.urlretrieve(argparse, file=lib + ".tar.gz")
    # extract
    lib_tar = tarfile.open(lib + ".tar.gz")
    lib_tar.extractall()
    lib_tar.close()
    # install
    os.chdir(lib_dir)
    subprocess.call(['python', 'setup.py', 'install', '--user'])
    os.chdir(HOME)
    # clean up
    shutil.rmtree(lib_dir)
    os.remove(lib_tar.name)

def main():
    # URLs
    argparse_url =\
        "http://pypi.python.org/packages/source/a/argparse/argparse-1.2.1.tar.gz"
    futures_url =\
        "http://pypi.python.org/packages/source/f/futures/futures-2.1.6.tar.gz"
    try:
        import argparse
    except ImportError:
        install("argparse", argparse_url)
    try:
        import concurrent.futures
    except ImportError:
        install("concurrent", futures_url)

if __name__ == '__main__':
    HOME = os.path.expanduser('~')
