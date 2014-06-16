#!/usr/bin/env python

"""
Processes a bam file by splitting it into it's regions and processing each
region in parallel. The workflow for each region is currently:

    [samtools view] -> [samtools mpileup] -> [VarScan]

Each region is added to a thread pool and the number of threads to run in
parallel can be controlled with a command line argument. There are two
'runnable' functions: one that writes to disk--and is thus slower--and one that
uses pipes; once again, which one is used can be determined by a command line
argument. The program needs two different configuration files, one to pass
arguments to `samtools mpileup` and another for VarScan. I tried to make this
program as modular as possible, the only function that I can think of that is
too monolithic is run_with_pipe, but that's just my opinion.

TODO
* improve comments
* use expanduser?
* improve variable names
* allow for stderr of programs to go to dev/null
* add a 'restart' command
"""

import subprocess
import os
import sys
from time import strftime
from multiprocessing import Lock
try:
    import pysam
    from argparse import ArgumentParser
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    print "please install the needed Python modules"
    sys.exit()

################################################################################
#                              utility functions
################################################################################

def append_file_name(file_name, to_add):
    """
    Creates a new file name with a string appended
    : file_name : the name of the file (as a string)
    : to_add : the string to add to file_name
    """
    (prefix, _) = file_name.split(".")
    return prefix + "." + to_add

def get_file_prefix(file_name):
    """
    Returns the file name without the extension
    i.e ~/User/Desktop/hello.txt -> hello
    :param file_name: the name of the file to extract the extension from
    """
    return file_name.split('/')[-1].split('.')[0]

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
    if args.verbose:
        print "> found sections: %s" % (', '.join(item for item in sections))
    return sections

def build_varscan_args(mpileup_f):
    """
    Parses a file containing the arguments for VarScan and returns a list for
    subprocess.open
    """

    args = ["java", "-jar", varscan_location, action]
    if not with_pipe:
        args.append(mpileup_f)
    LOCK.acquire()
    for line in varscan_conf:
        args.append(line.strip('\n'))

    LOCK.release()

    return args

def build_samtools_args(bam_f):
    """
    Parses a file containing the arguments for samtools mpileup and returns a
    list for subprocess.open. Unfortunately, it's very similar to
    build_varscan_args.
    """
    args = ["samtools", "mpileup"]
    if not with_pipe:
        args.append(bam_f)
    else:
        args.extend(["-", "-o", "-"])

    LOCK.acquire()
    for line in samtools_conf:
        args.append(line.strip('\n'))

    LOCK.release()

    return args

################################################################################
#                     functions that do the heavy lifting
################################################################################
def run(region):
    """
    Extracts the specific region and creates a mpileup file from that
    region, in turn this mpileup file is used to create a vcf file.
    """
    region_bam = create_bam(region)
    region_mpileup = create_mpileup(region, region_bam)
    create_vcf(region, region_mpileup)

    region_bam.close()
    region_mpileup.close()

def create_bam(region):
    """
    Creates a bam file from the passed region
    """
    bam_f = open(os.path.join(bam_dir, region + ".bam"), "w+b")
    if args.verbose:
        print "> %s creating %s" % (strftime(t_format), bam_f.name)
    subprocess.call(["samtools", "view", "-b", bam_file.filename, region],
        stdout=bam_f)
    if args.verbose:
        print "> %s FINISHED bam file for %s" % (strftime(t_format), region)

    return bam_f

def create_mpileup(region, bam_f):
    """
    Creates a mpileup file from the passed bam file
    """
    mpileup_f = open(os.path.join(mpileup_dir, region + ".mpileup"), "w+b")
    if args.verbose:
        print "> %s creating %s" % (strftime(t_format), mpileup_f.name)
    subprocess.call(build_samtools_args(bam_f.name), stdout=mpileup_f)
    if not args.keep_bam:
        os.remove(bam_f.name)
    if args.verbose:
        print "> %s FINISHED mpileup file for %s" % (strftime(t_format), region)

    return mpileup_f

def create_vcf(region, mpileup_f):
    """
    Runs VarScan on the mpileup file
    """
    vcf_f = open(os.path.join(vcf_dir, region + ".vcf"), "w+")
    if args.verbose:
        print "> %s creating vcf for %s" % (strftime(t_format), region)
    subprocess.call(build_varscan_args(mpileup_f.name), stdout=vcf_f)
    if not args.keep_mpileup:
        os.remove(mpileup_f.name)
    if args.verbose:
        print "> %s FINISHED vcf file for %s" % (strftime(t_format), region)

    vcf_f.close()

def run_with_pipe(region):
    """
    Runs the same commands as `run` but in a true pipeline
    """
    # it's important that the last command in the pipeline is evoked with
    # `subprocess.call`. If it's not, the program will terminate without waiting
    # for the processes to finish and you'll have to manually kill them.
    if args.verbose:
        print "> %s starting region %s" % (strftime(t_format), region)
    bam = subprocess.Popen(["samtools", "view", "-b", bam_file.filename, region],
        stdout=subprocess.PIPE)
    mpileup = subprocess.Popen(build_samtools_args(""), stdin=bam.stdout,
        stdout=subprocess.PIPE)
    vcf_f = open(os.path.join(vcf_dir, region + ".vcf"), "w+")
    subprocess.call(build_varscan_args(""), stdin=mpileup.stdout, stdout=vcf_f)

    # close the pipes
    bam.stdout.close()
    mpileup.stdout.close()

    if args.verbose:
        print "> %s FINISHED region %s" % (strftime(t_format), region)

def concat_vcfs(vcf_dir):
    """
    Concats all the vcf files created into a new file in the same directory.
    """
    arg_list = ["vcf-concat"]
    for vcf in os.listdir(vcf_dir):
        arg_list.append(os.path.join(vcf_dir, vcf))
    if args.verbose:
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
    # awesome ThreadPoolExecutor from Python 3. Allows you to control how many
    # concurrent processes are running at once. Useful in this program since
    # each region can use a lot of memory.
    if args.verbose:
        print "> parsing header sections"
    with ThreadPoolExecutor(max_workers=args.n_procs) as executor:
        for region in parse_header(infile):
            if not with_pipe:
                executor.submit(run, region)
            else:
                executor.submit(run_with_pipe, region)

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
    # conf files
    parser.add_argument("--varscan-conf", dest="varscan_conf", default=None,
        help="the location of varscan.conf (defaults to the working directory)")
    parser.add_argument("--samtools-conf", dest="samtools_conf", default=None,
        help="the location of samtools.conf (defaults to the working directory")
    # options
    parser.add_argument("--with-pipe", action="store_true", dest="with_pipe",
        help="instead of writing to disk, the commands are piped")
    parser.add_argument("--n-procs", dest="n_procs", default=None, type=int,
        help="the number of processes to run at once")
    parser.add_argument("--keep-bam", action="store_true", dest="keep_bam",
        help="keeps the intermediate bam files", default=False)
    parser.add_argument("--keep-mpileup", action="store_true", default=False,
        dest="keep_mpileup", help="keeps the intermediate mpileup files")
    parser.add_argument("--keep-all", action="store_true", dest="keep_all",
        help="keeps bam and mpileup files")
    parser.add_argument("--sort", action="store_true", dest="sort",
        help="use if the file needs to be sorted (implies --index)")
    parser.add_argument("--index", action="store_true", dest="index",
        help="use if the file needs to be indexed")
    parser.add_argument('-v', "--verbose", action="store_true", dest="verbose",
        help="output additional information")
    args = parser.parse_args()

    LOCK = Lock()

    bam_file = pysam.Samfile(str(args.infile), "rb")

    # global variables just to save some typing
    action = args.action
    with_pipe = args.with_pipe
    varscan_conf = args.varscan_conf
    samtools_conf = args.samtools_conf

    # test to see if a default varscan.conf and samtools.conf should be used
    # note: the files are returned to lists to avoid having to rewind them
    if varscan_conf == None:
        varscan_conf = open("varscan.conf", "r").readlines()
    if samtools_conf == None:
        samtools_conf = open("samtools.conf", "r").readlines()
    # test for PERL5LIB before any work is done
    #try:
    #    os.environ['PERL5LIB']
    #except KeyError:
    #    print "Please set your PERL5LIB environment variable"
    #    sys.exit()
    # test for a valid VarScan before any work is done as well
    if not os.path.exists(args.varscan_location):
        print "> VarScan location (%s) not valid" % (args.varscan_location)
        sys.exit()
    else:
        varscan_location = args.varscan_location
    # handle `--keep-all`
    if args.keep_all:
        args.keep_bam = True
        args.keep_mpileup = True
    if with_pipe:
        args.keep_bam = False
        args.keep_mpileup = False

    # append the name of the file to the dirs to avoid name conflicts
    bam_dir = "bam_" + get_file_prefix(bam_file.filename)
    mpileup_dir = "mpileup_" + get_file_prefix(bam_file.filename)
    vcf_dir = "vcf_" + get_file_prefix(bam_file.filename)
    t_format = '%H:%M:%S'

    # get the file ready for processing (if necessary)
    if args.sort:
        args.index = True
        sorted_file = append_file_name(bam_file.filename, "sorted")
        if args.verbose:
            print "> sorting %s for indexing" % (bam_file.filename)
            print "> creating %s" % (sorted_file)
        subprocess.call(["samtools", "sort", bam_file.filename, sorted_file])
    if args.index:
        if args.verbose:
            print "> indexing %s for viewing" % (bam_file.filename)
        subprocess.call(["samtools", "index", bam_file.filename])

    # create directories to avoid a messy working directory
    if not with_pipe:
        safe_mkdir(bam_dir)
        safe_mkdir(mpileup_dir)
    safe_mkdir(vcf_dir)

    run_processes(bam_file)

    # clean up (if necessary)
    if not args.keep_bam and not with_pipe:
        os.rmdir(bam_dir)
    if not args.keep_mpileup and not with_pipe:
        os.rmdir(mpileup_dir)
    bam_file.close()

#    concat_vcfs(vcf_dir)
