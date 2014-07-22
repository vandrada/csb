#!/usr/bin/env python

# install.py
# Copyright (C) 2014 Andrada, Vicente
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

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
    gets the would-be directory name from a pypi url.
    :param url: the url to extract the name from.
    """
    return '.'.join(url.split('/')[-1].split('.')[:-2])

def pip_install(lib):
    """
    Installs a library via pip.
    :param lib: the library to install.
    """
    subprocess.call(["pip", "install", lib, "--user"])
    print '\033[93m' + "installed " + lib + '\033[0m'

def install(lib, url):
    """
    Installs a library manually.
    :param lib: the library to install.
    :param url: the url of the the library to install.
    """
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
    if lib == "PyVCF":
        subprocess.call(["cython", "vcf/cparse.pyx"])
    subprocess.call(['python', 'setup.py', 'install', '--user'])
    os.chdir(HOME)
    # clean up
    shutil.rmtree(lib_dir)
    os.remove(lib_tar.name)
    print '\033[93m' + "installed " + lib + '\033[0m'

def main():
    # URLs
    pip_url =\
        "https://pypi.python.org/packages/source/p/pip/pip-1.5.6.tar.gz"
    pyvcf_url =\
        "https://pypi.python.org/packages/source/P/PyVCF/PyVCF-0.6.0.tar.gz"
    try:
        import pip
    except ImportError:
        install("pip", pip_url)
    try:
        import argparse
    except ImportError:
        pip_install("argparse")
    try:
        import concurrent.futures
    except ImportError:
        pip_install("futures")
    try:
        import cython
    except ImportError:
        pip_install("cython")
    try:
        import pysam
    except ImportError:
        pip_install("pysam")
    try:
        import xlrd
    except ImportError:
        pip_install("xlrd")
    try:
        import vcf
    except ImportError:
        # PyVcf doens't install correctly on RHEL so we have to do it manually
        # more info here: https://github.com/jamescasbon/PyVCF/issues/69
        install("PyVCF", pyvcf_url)
        pip_install("ordereddict")

if __name__ == '__main__':
    HOME = os.path.expanduser('~')
    main()
    print '\033[93m' + "All Python modules installed" + '\033[0m'
