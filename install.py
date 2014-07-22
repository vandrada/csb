#!/usr/bin/env python

"""
Installs the dependencies for all Python programs in this repo
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
    lib_dir = dir_name(url)
    print "installing %s to ~/%s" % (lib, lib_dir)
    urllib.urlretrieve(url, filename=lib + ".tar.gz")
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
    pip_url =\
        "https://pypi.python.org/packages/source/p/pip/pip-1.5.6.tar.gz"
    try:
        import pip
    except ImportError:
        install("pip", pip_url)
    try:
        import argparse
    except ImportError:
        subprocess.call(["pip", "install", "argparse", "--user"])
    try:
        import concurrent.futures
    except ImportError:
        subprocess.call(["pip", "install", "concurrent.futures", "--user"])
    try:
        import pysam
    except ImportError:
        subprocess.call(["pip", "install", "pysam", "--user"])
    try:
        import xlrd
    except ImportError:
        subprocess.call(["pip", "install", "xlrd", "--user"])
    try:
        import cython
    except ImportError:
        subprocess.call(["pip", "install", "cython", "--user"])
    try:
        import vcf
    except ImportError:
        subprocess.call(["pip", "install", "pyvcf", "--user"])

if __name__ == '__main__':
    HOME = os.path.expanduser('~')
    main()
    print "All Python modules installed"
