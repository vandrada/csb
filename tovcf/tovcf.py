#!/usr/bin/env python

import csv
import sys
import os
import time
import argparse
import xlrd

def create_csv(xls_file):
    """
    Creates a csv file from an Excel file.
    :param xls_file: the name of the Excel file
    :return: the name of the csv file
    ** Ripped off from Boud at StackOverflow **
    """
    csv_file = os.path.splitext(xls_file)[0] + ".csv"
    with xlrd.open_workbook(xls_file) as xls:
        sheet = xls.sheet_by_index(0)
        with open(csv_file, "wb") as f:
            c = csv.writer(f)
            for row in range(sheet.nrows):
                c.writerow(sheet.row_values(row))

    return csv_file

def header():
    """
    Creates the metadata lines and the header for the VCF file.
    :return: the metadata and the header as strings
    """
    # lines for the metadata
    meta =\
        ["fileformat=VCFv4.1",
         "fileDate={0}".format(time.strftime("%Y%m%d")),
         "source=tovcf",
         """FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">""",
         """FORMAT=<ID=COV,Number=1,Type=String,Description="Coverage">""",
         """FORMAT=<ID=QS,Number=1,Type=Integer,Description="Q Score">""",
         """FORMAT=<ID=TS,Number=1,Type=String,Description="Transcript">""",
         """FORMAT=<ID=CM,Number=1,Type=String,Description="c. Mutation">""",
         """FORMAT=<ID=PM,Number=1,Type=String,Description="p. Mutation">""",
         """FORMAT=<ID=OAS,Number=1,Type=String,Description="""
            """"1000Genome Allele Counts">""",
         """FORMAT=<ID=EAS,Number=1,Type=String,Description="""
            """"ESP Allele Counts">"""
        ]

    # standard header line
    head = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO",
            "FORMAT", "Sample1"]

    # add the '##' at the beginning and a newline at the end
    meta = ["##" + line + "\n" for line in meta]
    head = '\t'.join(head) + '\n'

    return ''.join(meta) + head

def genotype(ref, var):
    """
    Calculates the genotype from the reference allele and the variant allele(s).
    :param ref: the reference allele
    :param var: the variant allele(s)
    :return: a string for the genotype according to VCF spec (0/0, 0/1, etc.)
    """
    genotype = lambda allele: "0" if ref == allele else "1"
    alleles = list(var)

    return "{}/{}".format(*[genotype(allele) for allele in alleles])

def write_fields(in_file, out):
    """
    Transforms each line in the csv file to a VCF line and writes it to `out`.
    :param in_file: the csv file
    :param out: the location to write to
    """
    get = lambda field: '.' if row[FIELDS[field]] == 'NULL'\
                            else row[FIELDS[field]]

    create_record = lambda: ":".join([genotype(get("REF"), get("VAR")),
                                      get("COV"), get("QS"), get("TRANS"),
                                      get("CM"), get("PM"), get("OAS"),
                                      get("EAS")])

    line = ""
    record = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
    for row in in_file:
        line = record.format(get("CHR"), get("CO"), get("DB"), get("REF"),
                             get("VAR"), ".", ".", ".", FORMAT, create_record())
        out.write(line)

def process_xls(xls):
    """
    Converts a single xls file to a VCF file.
    :param xls: the xls file to process
    """
    csv_name = create_csv(xls)
    csv_file = csv.reader(open(csv_name, "r"))

    csv_file.next()     # read the first line and discard

    if args.to_stdout:
        out = sys.stdout
    else:
        out = open(os.path.splitext(csv_name)[0] + ".vcf", "w+")

    out.write(header())
    write_fields(csv_file, out)

    os.remove(csv_name)

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument("files", nargs='+',
        help="the xls(x) files to process")
    argparse.add_argument("--stdout", action="store_true", dest="to_stdout",
        help="output goes to stdout instead of a file")
    args = argparse.parse_args()

    # Constants
    FORMAT = "GT:COV:QS:TS:CM:PM:OAS:EAS"
    # fields from the csv
    cols = ["CHR", "CO", "REF", "VAR", "COV", "QS", "ZYG", "GENE", "TRANS",
            "CM", "PM", "DB", "OAS", "EAS"]
    FIELDS = dict(zip(cols, range(len(cols))))

    for xls in args.files:
        process_xls(xls)
