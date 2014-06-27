#!/usr/bin/env python

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
