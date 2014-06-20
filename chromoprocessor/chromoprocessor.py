#!/usr/bin/env python

import pysam
import sys
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from argparse import ArgumentParser

def s_print(mes, newline=True, pro='*'):
    if newline:
        sys.stdout.write(pro + " " + mes + "\n")
    else:
        sys.stdout.write(pro + " " + mes)

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

def make_dirs(sections):
    try:
        for section in sections:
            os.mkdir(section)
        os.mkdir(vcf_dir_name)
    except OSError:
        s_print("please remove the directories")
        sys.exit()

def read_conf_file(conf):
    try:
        with open(conf, "r") as f:
            return f.readlines()
    except IOError:
        s_print("%s not found" % (conf), pro="!")

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
    cmd = ["samtools", "mpileup"]
    for bamfile in bamfiles:
        cmd.append(bamfile)
    cmd.extend(["-o", "-"])

    lock.acquire()
    for line in SAMTOOLS_CONF:
        cmd.append(line.strip('\n'))
    lock.release()

    return cmd

def build_varscan_args():
    """
    Parses a file containing the arguments for VarScan and returns a list for
    subprocess.open
    :param mpileup_file_name: the name of the mpileup file to add as an argument
    :return: a list of arguments for subprocess
    """
    cmd = ["java", "-jar", args.location, args.action]

    lock.acquire()
    for line in VARSCAN_CONF:
        cmd.append(line.strip('\n'))
    lock.release()

    return cmd

def create_bam(bamfile, region):
    """
    Creates the bam file for each region
    :param bamfile: the bamfile to extract the region from
    :param region: the region to extract from the bamfile
    """
    outfile_name = os.path.join(region,
        region + "_" + get_filename(bamfile.filename) + ".bam")
    s_print("creating %s" %(outfile_name))
    outfile = open(outfile_name, "w+b")
    subprocess.call(
        ["samtools", "view", "-b", bamfile.filename, region], stdout=outfile)

def create_vcf(region):
    """
    call 'samtools mpileup' on all the files in a region and pipe the output to
    VarScan
    """
    # get all the bam files first!
    bamfiles = os.listdir(region)
    bamfiles = [os.path.join(region, bamf) for bamf in bamfiles]
    print bamfiles
    samtools_cmd = build_samtools_args(bamfiles)
    varscan_cmd = build_varscan_args()
    outfile_name = os.path.join(vcf_dir_name, region + ".vcf")
    varscan_file = open(outfile_name, "w+b")

    if args.verbose:
        s_print("calling: %s | %s > %s" % (' '.join(samtools_cmd),
        ' '.join(varscan_cmd), varscan_file.name))

    mpileup = subprocess.Popen(samtools_cmd, stdout=subprocess.PIPE)
    subprocess.call(varscan_cmd, stdin=mpileup.stdout, stdout=varscan_file)

    # remove the bam files
    for bamfile in bamfiles:
        os.remove(os.path.join(region, bamfile))

def run(region, bamfiles):
    if args.verbose:
        s_print("starting region %s" % (region))
    for bamfile in bamfiles:
        create_bam(bamfile, region)
    create_vcf(region)

def create_threads(bamfiles):
    with ThreadPoolExecutor(max_workers=args.n_region) as executor:
        for region in HEADER:
            executor.submit(run, region, bamfiles)

if __name__ == "__main__":
    parser = ArgumentParser()
    # arguments
    parser.add_argument("file_names",
        help="a file containing the names of the files to process")
    parser.add_argument("location",
        help="the location of the VarScan jar file")
    parser.add_argument("action",
        help="the action for VarScan to run")
    # options
    parser.add_argument("--n-region", type=int, dest="n_region", default=2,
        help="the number of regions to process in parallel")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    to_process = parse_file(args.file_names)    # the files to process
    bamfiles = []                               # samfile objects
    lock = multiprocessing.Lock()
    SAMTOOLS_CONF = read_conf_file("samtools.conf")
    VARSCAN_CONF = read_conf_file("varscan.conf")
    vcf_dir_name = "vcf"

    if to_process == []:
        s_print("exiting", pro="!")
        sys.exit()
    if args.verbose:
        s_print("found the following files: %s" % (', '.join(to_process)))

    # create the sam files
    for bamfile in to_process:
        bamfiles.append(pysam.Samfile(bamfile, "rb"))

    # make sure all the files have the same header and regions
    (valid, HEADER) = check_headers(bamfiles)
    if not valid:
        s_print("headers are not the same", pro="!")
        sys.exit()
    # make sure the VarScan location is valid
    if not os.path.exists(args.location):
        s_print("VarScan location (%s) not valid" % (args.location), pro="!")
        sys.exit()

    make_dirs(HEADER)
    create_threads(bamfiles)
