#!/usr/bin/env python

"""
Calls chromo_split on each bam file in the directory and adds them to the queue.
The default number of regions to process is 2 and the default number of bam
files to process is 2 as well, resulting in 4 concurrent processes at once.
"""

import concurrent.futures
from argparse import ArgumentParser
import os

parser = ArgumentParser()
parser.add_argument("directory", help="the directory to process")
parser.add_argument("--n-bam", default=2,
    help="the number of bam files to process in parallel")
parser.add_argument("--n-region", default=2,
    help="the number of regions to process in parallel")
args = parser.parse_args()

bam_files = []

for entry in os.listdir(args.directory):
    path = os.path.join(args.directory, entry)
    if not os.path.isdir(path):
        if path.split('.')[-1] == '.bam':
            bam_files.append(path)

print bam_files
