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
import argparse

def header():
    """
    Prints a fugly header.
    :param samples: the name of the samples to use in the header
    """
    head = "{0}\t{1}\t{2}\t{3}\n".\
        format("Chromosome", "Position", "Value", "Sample")
    head += '\n'

    return head

def parse(vcf_file, field):
    """
    Parses and prints specified fields from a vcf file.
    :param vcf_file: the vcf file to parse
    :param fields: the fields to parse and print from the vcf file.
    """

    # begin parsing (and printing)
    with open(field + ".txt", "w+") as out:
        out.write(header())
        for record in vcf_file:
            for sample in record:
                if sample[field] is None:
                    out.write("{0}\t{1}\t{2}\t{3}\n".
                              format(record.CHROM, record.POS, NA,
                                     sample.sample))
                else:
                    out.write("{0}\t{1}\t{2}\t{3}\n".
                              format(record.CHROM, record.POS,
                                     str(sample[field]), sample.sample))

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('vcf_file', help="the vcf file to parse")
    argparse.add_argument('fields', nargs='+', type=str,
        help="the sections to parse from the vcf file")
    args = argparse.parse_args()

    # feel free to change this
    NA = './.'

    for field in [field.upper() for field in args.fields]:
        vcf_file = vcf.Reader(open(args.vcf_file, 'r'))
        parse(vcf_file, field)
