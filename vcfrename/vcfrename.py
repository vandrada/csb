#!/usr/bin/env python

# vcfrename.py
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

import argparse
import sys

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('vcf_file', help="the vcf file to rename")
    argparse.add_argument('names', help="file with new names")
    args = argparse.parse_args()

    standard = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO",
                "FORMAT"]
    lines = []

    with open(args.names, "r") as names:
        for line in names:
            standard.append(line.replace('\n', ''))

    new_header = '\t'.join(standard) + '\n'

    with open(args.vcf_file, "r") as vcf_file:
        for line in vcf_file:
            if line.split('\t')[0] != "#CHROM":
                sys.stdout.write(line)
            else:
                sys.stdout.write(new_header)
