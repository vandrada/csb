#!/usr/bin/env python

import csv
import sys
import time
import argparse

def header():
    """
    Creates the metadata lines and the header for the VCF file.
    :return: the metadata and the header
    """
    # list of the header lines
    meta =\
        ["fileformat=VCFv4.1",
         "fileDate={0}".format(time.strftime("%Y%m%d")),
         """FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">""",
         """FORMAT=<ID=COV,Number=1,Type=Integer,Description="Coverage">""",
         """FORMAT=<ID=QS,Number=1,Type=Integer,Description="Q Score">""",
         """FORMAT=<ID=TS,Number=1,Type=String,Description="Transcript">""",
         """FORMAT=<ID=CM,Number=1,Type=String,Description="c. Mutation">""",
         """FORMAT=<ID=PM,Number=1,Type=String,Description="p. Mutation">""",
         """FORMAT=<ID=OAS,Number=1,Type=String,Description="1000Genome Allele Counts">""",
         """FORMAT=<ID=EAS,Number=1,Type=String,Description="ESP Allele Counts">"""
        ]

    head = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO",
            "FORMAT", "Sample1"]

    # add the '##' at the beginning and a newline at the end
    meta = ["##" + line + "\n" for line in meta]
    head = '\t'.join(head) + '\n'
    return (''.join(meta) + head)

def write_fields(in_file):
    """
    Transforms each line in the csv file to a VCF line.
    :param in_file: the csv file
    """
    # inner function just for the closure
    def get(field):
        item = row[FIELDS[field]]
        if item == 'NULL':
            return '.'
        else:
            return item

    def create_record():
        # TODO add GT
        return ":".join(["./.", get("cov"), get("qs"), get("trans"), get("cm"),
                        get("pm"), get("oas"), get("eas")])

    line = ""
    record = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
    for row in in_file:
        line = record.format(get("chr"), get("co"), get("db"), get("ref"),
                             get("var"), ".", ".", ".", FORMAT, create_record())
        sys.stdout.write(line)

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument("file", help="the csv file to process")
    args = argparse.parse_args()

    # constants
    FORMAT = "GT:COV:QS:TS:CM:PM:OAS:EAS"
    # fields from the csv
    cols = ["chr", "co", "ref", "var", "cov", "qs", "zyg", "gene", "trans",
            "cm", "pm", "db", "oas", "eas"]
    FIELDS = dict(zip(cols, range(len(cols))))

    in_file = csv.reader(open(args.file, "r"))
    # read the first line and discard
    in_file.next()

    sys.stdout.write(header())
    write_fields(in_file)
