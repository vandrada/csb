#!/usr/bin/env python

import vcf
import argparse

def header(samples, fields):
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

    parse(vcf_file, [field.upper() for field in args.fields])
