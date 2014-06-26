#!/usr/bin/env python

import vcf
import sys
import argparse

def header(samples, fields):
    """
    Prints a fugly header
    :param samples: the name of the samples to use in the header
    :param fields: the name of the fields to use in the header
    """
    f = ""
    for sample in samples:
        print SEP + "{0:15}".format(sample),
    print

    for field in fields:
        f += "{0:{1}} ".format(field, len(field))

    for sample in samples:
        print SEP + "{0:20}".format(f),
    print

def parse(vcf_file, fields):
    """
    Parses and prints specified fields from a vcf file
    :param vcf_file: the vcf file to parse
    :param fields: the fields to parse and print from the vcf file.
    """
    data = []
    samples = vcf_file.samples

    # header
    if args.pretty:
        header(samples, fields)

    # begin parsing (and printing)
    for record in vcf_file:
        if args.pretty:
            print "{0:4}:{1:10}".format(record.CHROM, str(record.POS)),
        for sample in record:
            if sample.called:
                for field in fields:
                    data.append(str(sample[field]))
            print "{0:30}".format(' '.join(data)),
            data = []
        print

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('vcf_file', help="the vcf file to parse")
    argparse.add_argument('--fields', nargs='+', type=str, default=[],
        help="the sections to parse from the vcf file")
    argparse.add_argument('--pretty', action="store_true",
        help="print a header and chromosome information")
    args = argparse.parse_args()

    SEP = '\t\t'
    vcf_file = vcf.Reader(open(args.vcf_file, 'r'))

    if not args.fields:
        print "no fields selected"
        sys.exit()

    parse(vcf_file, [field.upper() for field in args.fields])
