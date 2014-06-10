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
from multiprocessing import Process, Lock
from argparse import ArgumentParser

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

    args = ["java", "-jar", varscan_location, action]
    if not with_pipe:
        args.append(mpileup_f.name)
    LOCK.acquire()
    for line in arg_f:
        args.append(line.strip('\n'))

    # rewind the file to the beginning for future calls to build_varscan_args
    arg_f.seek(0)
    LOCK.release()

    return args

def run(region):
    """
    Extracts the specific region and creates a mpileup file from that
    region, in turn this mpileup file is used to create a vcf file.
    """
    region_bam = create_bam(region)
    region_mpileup = create_mpileup(region, region_bam)
    create_vcf(region, region_mpileup)

    # close the files
    region_bam.close()
    region_mpileup.close()


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

    vcf_f.close()

def run_with_pipe(region):
    """
    Runs the same commands as `run` but in a true pipeline
    """
    # it's important that the last command in the pipeline is evoked with
    # `subprocess.call`. If it's not, the program will terminate without waiting
    # for the processes to finish and you'll have to manually kill them.
    if verbose:
        print "> %s starting region %s" % (strftime(t_format), region)
    bam = subprocess.Popen(["samtools", "view", "-b", bam_file.filename, region],
        stdout=subprocess.PIPE)
    mpileup = subprocess.Popen(["samtools", "mpileup", "-", "-o", "-"],
        stdin=bam.stdout, stdout=subprocess.PIPE)
    vcf_f = open(os.path.join(vcf_dir, region + ".vcf"), "w+")
    subprocess.call(build_varscan_args(arg_f, ""), stdin=mpileup.stdout,
        stdout=vcf_f)

    # close the pipes
    bam.stdout.close()
    mpileup.stdout.close()

    if verbose:
        print "> %s FINISHED region %s" % (strftime(t_format), region)

def concat_vcfs(vcf_dir):
    """
    Concats all the vcf files created into a new file in the same directory.
    """
    arg_list = ["vcf-concat"]
    for vcf in os.listdir(vcf_dir):
        arg_list.append(os.path.join(vcf_dir, vcf))
    if verbose:
        print "%s running vcf_concat on the files in %s" %\
            (strftime(t_format), vcf_dir)
    # the new file has to be created after the relevant vcf files have been
    # added to the list, if it's created before very bad things happen
    vcf_file = open(os.path.join(vcf_dir, get_file_prefix(bam_file.filename) +
        ".vcf"), "w+")
    subprocess.call(arg_list, stdout=vcf_file)

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
        if with_pipe:
            process = Process(target=run_with_pipe, args=(region,))
        else:
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
    parser = ArgumentParser(description="Processes a bam file by region")
    # arguments
    parser.add_argument("infile",
        help="absolute path to the bam file to process")
    parser.add_argument("action",
        help="the action for VarScan to run")
    parser.add_argument("varscan_location",
        help="absolute path to the VarScan jar file")
    # options
    parser.add_argument("--with-pipe", action="store_true", dest="with_pipe",
        help="instead of writing to disk, the commands are piped")
    parser.add_argument("--keep-bam", action="store_true", dest="keep_bam",
        help="keeps the intermediate bam files", default=False)
    parser.add_argument("--keep-mpileup", action="store_true", default=False,
        dest="keep_mpileup", help="keeps the intermediate mpileup files")
    parser.add_argument("--keep-all", action="store_true", dest="keep_all",
        help="keeps bam and mpileup files")
    parser.add_argument("--varscan-conf", dest="varscan_conf", default=None,
        help="the location of varscan.conf (defaults to the working directory)")
    parser.add_argument("--sort", action="store_true", dest="sort",
        help="use if the file needs to be sorted (implies --index)")
    parser.add_argument("--index", action="store_true", dest="index",
        help="use if the file needs to be indexed")
    parser.add_argument('-v', "--verbose", action="store_true", dest="verbose",
        help="output additional information")
    args = parser.parse_args()

    LOCK = Lock()

    # global variables just to save some typing
    verbose = args.verbose
    keep_bam = args.keep_bam
    keep_mpileup = args.keep_mpileup
    action = args.action
    with_pipe = args.with_pipe
    arg_f = args.varscan_conf
    bam_file = pysam.Samfile(str(args.infile), "rb")

    # test to see if a default varscan.conf should be used
    if arg_f == None:
        arg_f = open("varscan.conf", "r")
    # test for PERL5LIB before any work is done
    try:
        os.environ['PERL5LIB']
    except KeyError:
        print "Please set your PERL5LIB environment variable"
        sys.exit()
    # test for a valid VarScan before any work is done as well
    if not os.path.exists(args.varscan_location):
        print "> VarScan location (%s) not valid" % (args.varscan_location)
        sys.exit()
    else:
        varscan_location = args.varscan_location
    # handle `--keep-all`
    if args.keep_all:
        keep_bam = True
        keep_mpileup = True
    if with_pipe:
        keep_bam = False
        keep_mpileup = False

    # append the name of the file to the dirs to avoid name conflicts
    bam_dir = "bam_" + get_file_prefix(bam_file.filename)
    mpileup_dir = "mpileup_" + get_file_prefix(bam_file.filename)
    vcf_dir = "vcf_" + get_file_prefix(bam_file.filename)
    t_format = '%H:%M:%S'

    # get the file ready for processing (if necessary)
    if args.sort:
        args.index = True
        sorted_file = append_file_name(bam_file, "sorted")
        if verbose:
            print "> sorting %s for indexing" % (bam_file.filename)
            print "> creating %s" % (sorted_file)
        subprocess.call(["samtools", "sort", bam_file.filename, sorted_file])
    if args.index:
        if verbose:
            print "> indexing %s for viewing" % (bam_file.filename)
        subprocess.call(["samtools", "index", bam_file.filename])

    # create directories to avoid a messy working directory
    if not with_pipe:
        safe_mkdir(bam_dir)
        safe_mkdir(mpileup_dir)
    safe_mkdir(vcf_dir)

    run_processes(bam_file)

    # clean up (if necessary)
    if not keep_bam and not with_pipe:
        os.rmdir(bam_dir)
    if not keep_mpileup and not with_pipe:
        os.rmdir(mpileup_dir)
    bam_file.close()

    concat_vcfs(vcf_dir)

