#!/usr/bin/env python

# vcfparse.py
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

import vcf
import sys
import argparse

def header(samples):
    """
    Prints a fugly header.
    :param samples: the name of the samples to use in the header
    """
    s = "{0}\t{1}\t".format("Chromosome", "Position")
    s += '\t'.join(samples)
    s += '\n'

    return s

def parse(vcf_file, field):
    """
    Parses and prints specified fields from a vcf file.
    :param vcf_file: the vcf file to parse
    :param fields: the fields to parse and print from the vcf file.
    """
    samples = vcf_file.samples

    # begin parsing (and printing)
    out = open(field + ".txt", "w+")
    out.write(header(samples))

    for record in vcf_file:
        out.write("{0}\t{1}".format(record.CHROM, record.POS))
        for sample in record:
            if sample[field] == None:
                out.write('\t{0}'.format(NA))
            else:
                out.write('\t{0}'.format(str(sample[field])))
        out.write('\n')

    out.close()

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('vcf_file', help="the vcf file to parse")
    argparse.add_argument('fields', nargs='+', type=str,
        help="the sections to parse from the vcf file")
    args = argparse.parse_args()

    NA = './.'

    for field in [field.upper() for field in args.fields]:
        vcf_file = vcf.Reader(open(args.vcf_file, 'r'))
        parse(vcf_file, field)
