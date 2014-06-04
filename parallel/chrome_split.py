#!/usr/bin/env python

import pysam
import subprocess
import os
from multiprocessing import Process
from optparse import OptionParser

def run(region):
    """
    Extracts the specific region and creates a mpileup file from that
    region.
    """
    region_bam_file = create_bam(region)
    region_mpileup_file = create_mpileup(region, region_bam_file)

    # TODO run varscan

def create_bam(region):
    """
    Creates a bam file from the passed region
    """
    region_bam = open(os.path.join(bam_dir, region + ".bam"),
        "w+b")
    if (verbose):
        print "> creating %s" %(region_bam.name)
    subprocess.call(["samtools", "view", "-b", bam_file.filename, region],
            stdout=region_bam)
    if (verbose):
        print "> FINISHED %s" %(region_bam.name)

    return region_bam

def create_mpileup(region, region_bam_file):
    """
    Creates a mpileup file from the passed bam file
    """
    region_mpileup =\
        open(os.path.join(mpileup_dir, region + ".mpileup"), "w+b")
    if (verbose):
        print "> creating %s" %(region_mpileup.name)
    subprocess.call(["samtools", "mpileup", region_bam_file.name],
        stdout=region_mpileup)
    if (verbose):
        print "> FINISHED %s" %(region_mpileup.name)

def parse_header(samfile):
    """
    Returns the sections from 'samfile'
    :param samfile: the sam file to parse
    """
    sections = [SN['SN'] for SN in samfile.header['SQ']]
    if (verbose):
        print "> found sections: %s" % ', '.join(item for item in sections)
    return sections

def append_file_name(samfile, to_add="sorted"):
    (prefix, suffix) = samfile.filename.split(".")
    return prefix + "." + to_add

def get_file_prefix(samfile):
    return samfile.split('/')[-1].split('.')[0]

def run_processes(infile):
    """
    Function to spawn and join the threads.
    :param infile: the original .bam file to use
    """
    processes = []
    if (verbose):
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
    # Parse the command line arguments
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="infile",
        help="absolute path to the bam file to process")
    parser.add_option("--index", action="store_true", dest="index",
        help="use if the file needs to be indexed")
    parser.add_option("--sort", action="store_true", dest="sort",
        help="use if the file needs to be sorted (implies --index)")
    parser.add_option('-v', "--verbose", action="store_true", dest="verbose",
        help="output additional information")
    (options, args) = parser.parse_args()

    verbose = options.verbose

    bam_file = pysam.Samfile(str(options.infile), "rb")
    # append the name of the file to the dir to avoid name conflicts
    bam_dir = "bam" + "_" + get_file_prefix(bam_file.filename)
    mpileup_dir = "mpileup" + "_" + get_file_prefix(bam_file.filename)

    if (options.sort):
        options.index = True
        sorted_file = append_file_name(bam_file)
        if (verbose):
            print "> sorting %s for indexing" % (bam_file.filename)
            print "> creating %s" % (sorted_file)
        subprocess.call(["samtools", "sort", bam_file.filename,
            append_file_name(bam_file)])
        # we need to append .bam since samtools takes the new prefix not the
        # new file name
        bam_file = pysam.Samfile(sorted_file + ".bam")
    if (options.index):
        if (verbose):
            print "> indexing %s for viewing" % (bam_file.filename)
        subprocess.call(["samtools", "index", bam_file.filename])

    os.mkdir(bam_dir)
    os.mkdir(mpileup_dir)

    run_processes(bam_file)
