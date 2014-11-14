#!/usr/bin/env python

# chromoprocessor.py
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
Processes multiple BAM files in parallel by splitting them into regions.
"""

import re
import os
import sys
import time
import subprocess
import multiprocessing
try:
    import pysam
    from concurrent.futures import ThreadPoolExecutor
    from argparse import ArgumentParser
except ImportError:
    print "please install the needed Python modules"


def s_print(mes, newline=True, pro='*'):
    """
    prints to stdout with a prologue
    :param mes: the message to print to stdout
    :param newline: whether or not to print a new line. The default is True.
    :param pro: the prologue to precede mes. The default is '*'
    """
    t_form = "%H:%M:%S"
    LOCK.acquire()
    sys.stdout.write('\033[34m' + pro + '[' + time.strftime(t_form) + ']' +
                     mes + '\033[0m')
    if newline:
        sys.stdout.write("\n")
    LOCK.release()


def extract_header(samfile):
    """
    Extracts the regions from the BAM file
    :param samfile: the BAM file to extract the headers from
    """
    sections = [SQ['SN'] for SQ in samfile.header['SQ']]
    return sections


def get_filename(samfile):
    """
    Extracts the name of the file
    :param samfile: the name of the file to extract
    :return: the name of the file
    """
    return samfile.split('/')[-1].split('.')[0]


def natural_sort(l):
    """
    Sorts a list naturally--the way that a human will sort it--in place.
    From http://blog.codinghorror.com/sorting-for-humans-natural-sort-order
    :param l: the list to sort
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    l.sort(key=alphanum_key)


def check_input():
    """
    Ensures that input is entered and only one input source is specified.
    """
    # no input specified
    if ARGS.file_name is None and ARGS.dir is None and ARGS.bam == []:
        s_print("no input provided", pro=ERR)
        sys.exit()
    # multiple input
    elif ARGS.file_name is not None and ARGS.dir is not None:
        s_print("input can only come from one source", pro=ERR)
        sys.exit()
    elif ARGS.file_name is not None and ARGS.bam != []:
        s_print("input can only come from one source", pro=ERR)
        sys.exit()
    elif ARGS.dir is not None and ARGS.bam != []:
        s_print("input can only come from one source", pro=ERR)
        sys.exit()


def check_command(prog):
    """
    Checks if prog exists in path using `which`. NOT PORTABLE
    :param prog: the command to check for
    """
    try:
        with open(os.devnull) as out:
            subprocess.check_call(['which', prog], stdout=out)
    except subprocess.CalledProcessError:
        s_print("%s not found in path" % prog, pro=ERR)
        sys.exit()


def check_external_commands():
    """
    Ensures that all programs that are needed are in the path or, in the case
    of VarScan, that the passed in location is valid.
    """
    # check for PERL5LIB in path
    try:
        os.environ['PERL5LIB']
    except KeyError:
        s_print("Please set your PERL5LIB environment variable", pro=ERR)
        sys.exit()

    # check for samtools and vcf-concat
    check_command('samtools')
    check_command('vcf-concat')

    # make sure the VarScan location is valid
    if not os.path.exists(ARGS.location):
        s_print("VarScan location (%s) not valid" % (ARGS.location), pro=ERR)
        sys.exit()


def parse_input():
    """
    Parses the correct input source and returns the contents
    """
    if ARGS.file_name:
        return parse_file(ARGS.file_name)
    elif ARGS.dir:
        return parse_dir(ARGS.dir)
    else:
        return ARGS.bam


def parse_file(file_with_bams):
    """
    Returns a list of the files that need to be processed.
    :param file_with_bams: a file containing the name of the files to process.
    :return: an empty list if an error occurs, else a list with the files.
    """
    files = open(file_with_bams, "r")
    lines = files.readlines()
    files.close()

    # sanity check...
    for line in lines:
        if line.strip('\n').split('.')[-1] != 'bam':
            s_print("%s is not a BAM file" % (line.strip('\n')), pro=ERR)
            lines.remove(line)

    return [line.strip('\n') for line in lines]


def parse_dir(dir_with_bams):
    """
    Returns a list of BAM files from a directory
    :param dir_with_bams: the directory to gather the BAM files from
    :return: a list of BAM files
    """
    return [os.path.join(root, bam_file)
            for root, _, files in os.walk(dir_with_bams)
            for bam_file in files
            if bam_file.split('.')[-1] == 'bam']


def make_dirs(sections, vcf_dir_name):
    """
    Attempts to make the dirs that are needed throughout the course of the
    program. In order to keep the working directory relatively clean this
    program creates a directory for each region in the BAM files and one for
    the VCF files.
    :param sections: a list containing the names of the directories
    :param vcf_dir_name: the name of the directory to hold the VCF files.
    """
    try:
        for section in sections:
            os.mkdir(section)
        os.mkdir(vcf_dir_name)
    except OSError:
        s_print("please remove the directories", pro=ERR)
        sys.exit()


def read_conf_file(conf):
    """
    Reads a conf file and returns the contents.
    :param conf: the conf file to read
    :return: a list of the lines in the file
    """
    try:
        with open(conf, "r") as conf_file:
            return conf_file.readlines()
    except IOError:
        # no conf file found
        s_print("%s not found; using default arguments" % (conf))
        return []


def check_headers(bamfiles):
    """
    Ensures that all the BAM files have the same sections
    :param bamfiles: a list of BAM files
    :return: a tuple where the first element is True if all the headers are the
    same and False otherwise, and the second element is the header of the first
    BAM file.
    """
    # get the first header and use it to compare against
    master = extract_header(bamfiles[0])
    return (all([extract_header(bam) == master for bam in bamfiles]), master)


def append_arguments(cmd, conf):
    """
    Append options from conf to a command to be called with subprocess
    :param cmd: the command list
    :param conf: the conf file holding the options
    """
    if conf:
        LOCK.acquire()
        for line in conf:
            cmd.extend(line.strip('\n').split(' '))
        LOCK.release()


def build_samtools_args(bamfiles, samtools_conf):
    """
    Parses a file containing the arguments for `samtools mpileup` and returns a
    list for subprocess.open.
    :param bamfiles: a list of the BAM files to add to the command.
    :param samtools_conf: a file with the options to pass to samtools.
    :return: a list of arguments for the `samtools mpileup` command.
    """
    cmd = ["samtools", "mpileup"]
    cmd.extend(bamfiles)
    cmd.extend(["-o", "-"])

    append_arguments(cmd, samtools_conf)

    return cmd


def build_varscan_args(varscan_conf):
    """
    Parses a file containing the arguments for VarScan and returns a list for
    subprocess.open
    :param varscan_conf: a file with the options to pass to VarScan.
    :return: a list of arguments for the VarScan subprocess
    """
    # No filenames are needed because it's piped
    cmd = ["java", "-jar", ARGS.location, ARGS.action, "--output-vcf", "1"]

    append_arguments(cmd, varscan_conf)

    return cmd


def create_bam(bamfile, region):
    """
    Creates the BAM file for each region. File names will have a form similar
    to 'chr1/chr1_sample.bam'.
    :param bamfile: the BAM file to extract the region from
    :param region: the region to extract from the BAM file from.
    """
    outfile_name = os.path.join(region, region + "_" +
                                get_filename(bamfile.filename) + ".bam")
    s_print("creating %s" % (outfile_name))
    outfile = open(outfile_name, "w+b")
    subprocess.call(["samtools", "view", "-b", bamfile.filename, region],
                    stdout=outfile)


def create_vcf(region, vcf_dir_name, samtools_conf, varscan_conf):
    """
    Calls `samtools mpileup` on all the files in a region and pipes the output
    to VarScan. File names will have a form similar to 'vcf/chr1.vcf'.
    :param region: the region to process
    :param vcf_dir_name: the name of the directory to hold the VCF files.
    :param samtools_conf: a file with the options to pass to samtools.
    :param varscan_conf: a file with the options to pass to VarScan.
    """
    # get all the BAM files first
    input_files = os.listdir(region)
    natural_sort(input_files)
    bamfiles = [os.path.join(region, bamf) for bamf in input_files]

    samtools_cmd = build_samtools_args(bamfiles, samtools_conf)
    varscan_cmd = build_varscan_args(varscan_conf)
    outfile_name = os.path.join(vcf_dir_name, region + ".vcf")
    varscan_file = open(outfile_name, "w+b")

    if ARGS.verbose:
        s_print("calling: \n%s | %s > %s" % (' '.join(samtools_cmd),
                ' '.join(varscan_cmd), varscan_file.name))

    mpileup = subprocess.Popen(samtools_cmd, stdout=subprocess.PIPE)
    subprocess.call(varscan_cmd, stdin=mpileup.stdout, stdout=varscan_file)

    # remove the BAM files
    for bamfile in bamfiles:
        os.remove(bamfile)

    # and finally remove the directory
    try:
        os.rmdir(region)
    except OSError:
        s_print("%s not empty" % (region), pro=ERR)


def concat_vcfs(vcf_dir):
    """
    Concatenates all the VCF files in a directory
    :param vcf_dir: the directory with the VCF files
    """
    arglist = ["vcf-concat"]
    for vcf in os.listdir(vcf_dir):
        arglist.append(os.path.join(vcf_dir, vcf))
    if ARGS.verbose:
        s_print("running vcf-concat on the files in %s" % vcf_dir)

    with open(ARGS.out, "w+") as vcf_file:
        subprocess.call(arglist, stdout=vcf_file)

    # clean up
    for vcf in os.listdir(vcf_dir):
        os.remove(os.path.join(vcf_dir, vcf))
    try:
        os.rmdir(vcf_dir)
    except OSError:
        s_print("%s not empty" % vcf_dir, pro=ERR)


def run(region, bamfiles, vcf_dir_name, samtools_conf, varscan_conf):
    """
    Super generic name, but this function does the bulk of the work. It creates
    the BAM files and then creates the VCF files.
    :param region: the region to process
    :param bamfile: a list of BAM files to process
    :param vcf_dir_name: the name of the directory to hold the VCF files.
    :param samtools_conf: a file with the options to pass to samtools.
    :param varscan_conf: a file with the options to pass to VarScan.
    """
    if ARGS.verbose:
        s_print("starting region %s" % (region))
    for bamfile in bamfiles:
        create_bam(bamfile, region)
    create_vcf(region, vcf_dir_name, samtools_conf, varscan_conf)


def create_threads(bamfiles, header, vcf_dir_name, samtools_conf,
                   varscan_conf):
    """
    Creates the threads to handle the individual regions.
    :param bamfiles: a list of BAM files to process
    :param header: the header of the VCF files
    :param vcf_dir_name: the name of the directory to hold the VCF files.
    :param samtools_conf: a file with the options to pass to samtools.
    :param varscan_conf: a file with the options to pass to VarScan.

    """
    with ThreadPoolExecutor(max_workers=ARGS.n_region) as executor:
        for region in header:
            executor.submit(run, region, bamfiles, vcf_dir_name, samtools_conf,
                            varscan_conf)


def main():
    """
    Main method
    """
    vcf_dir_name = "vcf"
    check_input()
    check_external_commands()

    samtools_conf = read_conf_file("samtools.conf")
    varscan_conf = read_conf_file("varscan.conf")
    to_process = parse_input()

    # check if the files are valid
    if to_process == []:
        s_print("no files found; exiting", pro=ERR)
        sys.exit()
    if ARGS.verbose:
        s_print("found the following files: %s" % (', '.join(to_process)))

    # create the BAM files
    bamfiles = [pysam.Samfile(bam, "rb") for bam in to_process]

    # make sure all the files have the same header and regions
    (valid, header) = check_headers(bamfiles)
    if not valid:
        s_print("headers are not the same", pro=ERR)
        sys.exit()

    natural_sort(header)

    make_dirs(header, vcf_dir_name)
    create_threads(bamfiles, header, vcf_dir_name, samtools_conf, varscan_conf)
    concat_vcfs(vcf_dir_name)


if __name__ == '__main__':
    ERR = '!'
    LOCK = multiprocessing.Lock()
    PARSER = ArgumentParser()
    # arguments
    # specifying the file(s)
    PARSER.add_argument(
        "--file", dest="file_name", default=None,
        help="a file containing the names of the files to process")
    PARSER.add_argument(
        "--dir", dest="dir", default=None,
        help="the directory containing the BAM files")
    PARSER.add_argument(
        "--list", dest="bam", nargs='+', default=[],
        help="a list of the BAM files")
    # other
    PARSER.add_argument(
        "location",
        help="the location of the VarScan jar file")
    PARSER.add_argument(
        "action",
        help="the action for VarScan to run")
    # options
    PARSER.add_argument(
        "--out", dest="out", default="run.vcf",
        help="the name of the output VCF file")
    PARSER.add_argument(
        "--n-region", type=int, dest="n_region", default=2,
        help="the number of regions to process in parallel")
    PARSER.add_argument(
        "--verbose", "-v", action="store_true")
    ARGS = PARSER.parse_args()

    main()
