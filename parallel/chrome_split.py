#!/usr/bin/env python

import pysam
import subprocess
import threading
import os
from optparse import OptionParser

class runner(threading.Thread):
    def __init__(self, region, threadID=0, name=""):
        """
        Creates a new runner object
        :param region: the region to extract from the bam file
        :param threadID: the ID of this thread, defaults to 0
        :param name: the name of this thread, defaults to ""
        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.region = region

    def run(self):
        """
        Extracts the specific region and creates a mpileup file from that
        region.
        """
        # create the bam file
        current_bam_file = open(os.path.join(bam_dir, self.region + ".bam"),
            "w+b")
        if (verbose):
            print "> creating %s" %(current_bam_file.name)
        subprocess.call(["samtools", "view", "-b", bam_file.filename, self.region],
                stdout=current_bam_file)
        if (verbose):
            print "> done with %s" %(current_bam_file.name)

        # create the mpileup file
        current_mpileup_file =\
            open(os.path.join(mpileup_dir, self.region + ".mpileup"), "w+b")
        if (verbose):
            print "> creating %s" %(current_mpileup_file.name)
        subprocess.call(["samtools", "mpileup", current_bam_file.name],
            stdout=current_mpileup_file)
        if (verbose):
            print "> done with %s" %(current_mpileup_file.name)

        # TODO run varscan

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

def run_threads(infile):
    """
    Function to spawn and join the threads.
    :param infile: the original .bam file to use
    """
    threads = []
    if (verbose):
        print "> parsing header sections"
    for region in parse_header(infile):
        current_thread = runner(region)
        threads.append(current_thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

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
    bam_dir = "bam"
    mpileup_dir = "mpileup"

    bam_file = pysam.Samfile(str(options.infile), "rb")

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

    run_threads(bam_file)
