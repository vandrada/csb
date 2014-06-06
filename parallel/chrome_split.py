#!/usr/bin/env python

import subprocess
import os
import sys
try:
    import pysam
except ImportError:
    print "please install pysam"
    sys.exit()
from time import strftime
from multiprocessing import Process
from optparse import OptionParser

def append_file_name(samfile, to_add):
    """
    Creates a new file name with a string appended
    """
    (prefix, _) = samfile.filename.split(".")
    return prefix + "." + to_add

def get_file_prefix(samfile):
    """
    Returns the file name without the extension
    i.e ~/User/Desktop/hello.txt -> hello
    """
    return samfile.split('/')[-1].split('.')[0]

def safe_mkdir(dirname):
    """
    Attempts to make a directory with the name `dirname`. If a directory already
    exists with that name, the program exits gracefully with a nice message.
    """
    try:
        os.mkdir(dirname)
    except OSError:
        print "please remove/rename/move %s" % (dirname)
        sys.exit()

def parse_header(samfile):
    """
    Returns the sections from 'samfile'
    """
    sections = [SQ['SN'] for SQ in samfile.header['SQ']]
    if verbose:
        print "> found sections: %s" % (', '.join(item for item in sections))
    return sections

def build_varscan_args(arg_f, mpileup_f):
    """
    Parses a file containing the arguments for VarScan and returns a list for
    subprocess.open
    """
    args = ["java", "-jar", varscan_location, action, mpileup_f.name]
    for line in arg_f:
        args.append(line.strip('\n'))

    # rewind the file to the beginning for future calls to build_varscan_args
    arg_f.seek(0)

    return args

def run(region):
    """
    Extracts the specific region and creates a mpileup file from that
    region, in turn this mpileup file is used to create a vcf file.
    """
    region_bam = create_bam(region)
    region_mpileup = create_mpileup(region, region_bam)
    create_vcf(region, region_mpileup)

def create_bam(region):
    """
    Creates a bam file from the passed region
    """
    bam_f = open(os.path.join(bam_dir, region + ".bam"), "w+b")
    if verbose:
        print "> %s creating %s" % (strftime(t_format), bam_f.name)
    subprocess.call(["samtools", "view", "-b", bam_file.filename, region],
        stdout=bam_f)
    if verbose:
        print "> %s FINISHED bam file for %s" % (strftime(t_format), region)

    return bam_f

def create_mpileup(region, bam_f):
    """
    Creates a mpileup file from the passed bam file
    """
    mpileup_f = open(os.path.join(mpileup_dir, region + ".mpileup"), "w+b")
    if verbose:
        print "> %s creating %s" % (strftime(t_format), mpileup_f.name)
    subprocess.call(["samtools", "mpileup", bam_f.name], stdout=mpileup_f)
    if not keep_bam:
        os.remove(bam_f.name)
    if verbose:
        print "> %s FINISHED mpileup file for %s" % (strftime(t_format), region)

    return mpileup_f

def create_vcf(region, mpileup_f):
    """
    Runs VarScan on the mpileup file
    """
    vcf_f = open(os.path.join(vcf_dir, region + ".vcf"), "w+")
    if verbose:
        print "> %s creating vcf for %s" % (strftime(t_format), region)
    subprocess.call(build_varscan_args(arg_f, mpileup_f), stdout=vcf_f)
    if not keep_mpileup:
        os.remove(mpileup_f.name)
    if verbose:
        print "> %s FINISHED vcf file for %s" % (strftime(t_format), region)

def run_processes(infile):
    """
    Function to spawn and join the processes
    """
    # Note: I debated for a while whether to use multiprocessing or threading,
    # ultimately I decided on the multiprocessing module since each process runs
    # in its own memory space and there aren't any shared variables.  Also, I
    # read somewhere that processes are cheaper on Linux and OS X than threads.
    # I don't know how true that is, and with that being said it's bad that that
    # made an impact on my decision, but that's the truth.
    processes = []
    if verbose:
        print "> parsing header sections"
    for region in parse_header(infile):
        process = Process(target=run, args=(region,))
        # to prevent orphans
        process.daemon = True
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    # parse the command line arguments
    parser = OptionParser()
    # needed arguments
    parser.add_option("-f", "--file", dest="infile",
        help="absolute path to the bam file to process")
    parser.add_option("--varscan", dest="varscan_location",
        help="absolute path to the VarScan jar file")
    parser.add_option("--action", dest="action",
        help="the action for VarScan to run")
    # options
    parser.add_option("--keep-bam", action="store_true", dest="keep_bam",
        help="keeps the intermediate bam files", default=False)
    parser.add_option("--keep-mpileup", action="store_true", default=False,
        dest="keep_mpileup", help="keeps the intermediate mpileup files")
    parser.add_option("--keep-all", action="store_true", dest="keep_all",
        help="keeps bam and mpileup files")
    parser.add_option("--varscan-conf", dest="varscan_conf", default=None,
        help="the location of varscan.conf (defaults to the working directory)")
    parser.add_option("--sort", action="store_true", dest="sort",
        help="use if the file needs to be sorted (implies --index)")
    parser.add_option("--index", action="store_true", dest="index",
        help="use if the file needs to be indexed")
    parser.add_option('-v', "--verbose", action="store_true", dest="verbose",
        help="output additional information")
    (options, args) = parser.parse_args()

    # global variables just to save some typing
    verbose = options.verbose
    keep_bam = options.keep_bam
    keep_mpileup = options.keep_mpileup
    if options.keep_all:
        keep_bam = True
        keep_mpileup = True
    if not os.path.exists(options.varscan_location):
        print "> VarScan location (%s) not valid" % (options.varscan_location)
        sys.exit()
    else:
        varscan_location = options.varscan_location
    action = options.action
    arg_f = options.varscan_conf
    if arg_f == None:
        arg_f = open("varscan.conf", "r")

    bam_file = pysam.Samfile(str(options.infile), "rb")
    # append the name of the file to the dir to avoid name conflicts
    bam_dir = "bam_" + get_file_prefix(bam_file.filename)
    mpileup_dir = "mpileup_" + get_file_prefix(bam_file.filename)
    vcf_dir = "vcf_" + get_file_prefix(bam_file.filename)
    t_format = '%H:%M:%S'

    # get the file ready for processing (if necessary)
    if options.sort:
        options.index = True
        sorted_file = append_file_name(bam_file, "sorted")
        if verbose:
            print "> sorting %s for indexing" % (bam_file.filename)
            print "> creating %s" % (sorted_file)
        subprocess.call(["samtools", "sort", bam_file.filename, sorted_file])
    if options.index:
        if verbose:
            print "> indexing %s for viewing" % (bam_file.filename)
        subprocess.call(["samtools", "index", bam_file.filename])

    # create directories to avoid a messy working directory
    safe_mkdir(bam_dir)
    safe_mkdir(mpileup_dir)
    safe_mkdir(vcf_dir)

    run_processes(bam_file)

    # clean up (if necessary)
    if not keep_bam:
        os.rmdir(bam_dir)
    if not keep_mpileup:
        os.rmdir(mpileup_dir)
