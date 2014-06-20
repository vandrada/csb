#!/usr/bin/env python

import pysam
import sys
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from argparse import ArgumentParser

def s_print(mes, newline=True):
    if newline:
        sys.stdout.write("* " + mes + "\n")
    else:
        sys.stdout.write(mes)

def extract_header(samfile):
    """
    Extracts the regions from the bam file
    :param bam_file: the bam file to extract the headers from
    """
    sections = [SQ['SN'] for SQ in samfile.header['SQ']]
    return sections

def get_filename(samfile):
    """
    Extracts the name of the file
    :param samfile: the name of the file to extract
    :return: the name of the file
    """
    return samfile.split('.')[0]

def parse_file(file_with_bams):
    """
    Returns a list of the files that need to be processed
    :return: an empty list if an error occurs, else a list with the files
    """
    files = open(file_with_bams, "r")
    lines = files.readlines()
    files.close()

    # sanity check...
    for line in lines:
        if line.strip('\n').split('.')[-1] != 'bam':
            s_print("%s is not a bam file" % (line))
            return []

    return map(lambda file_name: file_name.strip('\n'), lines)

def make_dir(sections):
    try:
        for section in sections:
            os.mkdir(section)
    except OSError:
        s_print("please remove the directories")
        sys.exit()

def check_headers(bamfiles):
    """
    Ensures that all the bamfiles have the same sections
    :param bamfiles: a list of bam files
    :return: True if the headers all the same, False otherwise
    """
    # get the first header and use it as a comparator
    master = extract_header(bamfiles[0])
    return (all(map(lambda h: extract_header(h) == master, bamfiles)), master)

def build_samtools_args(bamfiles):
    """
    Parses a file containing the arguments for `samtools mpileup` and returns a
    list for subprocess.open. Unfortunately, it's very similar to
    build_varscan_args.
    :param bam_file_name: the name of the bam file to add as an argument
    :return: a list of arguments for subprocess
    """
    args = ["samtools", "mpileup"]
    for bamfile in bamfiles:
        args.append(bamfile)
    args.extend(["-o", "-"])

    lock.acquire()
    for line in SAMTOOLS_CONF:
        args.append(line.strip('\n'))

    lock.release()

    return args

def create_bam(bamfile, region):
    """
    Creates the bam file for each region
    :param bamfile: the bamfile to extract the region from
    :param region: the region to extract from the bamfile
    """
    outfile_name = os.path.join(region, get_filename(bamfile.filename) + ".bam")
    s_print("creating %s" %(outfile_name))
    outfile = open(outfile_name, "w+b")
    subprocess.call(
        ["samtools", "view", "-b", bamfile.filename, region], stdout=outfile)

def create_vcf(region):
    """
    call 'samtools mpileup' on all the files in a region and pipe the output to 
    VarScan
    """
    bamfiles = os.listdir(region)
    cmd = build_samtools_args(bamfiles)
    if args.verbose:
        s_print("%s: calling '" + ' '.join(arg for arg in cmd) + "'" % (region))
    mpileup = open(os.path.join(region, region + ".mpileup"), "w+b")
    subprocess.call(build_samtools_args(bamfiles), stdout=mpileup)

    # remove the bam files
    for bamfile in region:
        os.remove(os.path.join(region, bamfile))

def run(region, bamfiles):
    if args.verbose:
        s_print("starting region %s" % (region))
    for bamfile in bamfiles:
        create_bam(bamfile, region)
    create_vcf(region)

def create_threads(bamfiles):
    with ThreadPoolExecutor(max_workers=2) as executor:
        for region in HEADER:
            executor.submit(run, region, bamfiles)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("file_names",
        help="a file containing the names of the files to process")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    to_process = parse_file(args.file_names)    # the files to process
    bamfiles = []                               # samfile objects
    lock = multiprocessing.Lock()
    SAMTOOLS_CONF = []

    if to_process == []:
        s_print("exiting")
        sys.exit()
    if args.verbose:
        s_print("found the following files: %s" % (', '.join(to_process)))

    # create the sam files
    for bamfile in to_process:
        bamfiles.append(pysam.Samfile(bamfile, "rb"))

    # make sure all the files have the same header and regions
    (valid, HEADER) = check_headers(bamfiles)
    if not valid:
        s_print("headers are not the same")
        sys.exit()

    # open conf files
    with open("samtools.conf", "r") as f:
        SAMTOOLS_CONF.extend(f.readlines())

    make_dir(HEADER)
    create_threads(bamfiles)
