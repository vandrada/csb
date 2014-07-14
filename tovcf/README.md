# Name
tovcf

# Description
Transfroms an Excel file to a VCF file.

# Dependencies
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>

* [xlrd](https://pypi.python.org/pypi/xlrd)

# Synopsis
usage:

    tovcf file.xls [file2.xls ...] [-h] [--stdout]

## Arguments
* `file.xls`: one or more Excel files to convert to a VCF file. xlsx files are
also supported.

## Options
* `--stdout`: send output to stdout. The default behavior is to send the output
to a file with the same name as the xls file, but with an extension of vcf.

# Examples
To create a file named `input.vcf` simply call

    tovcf input.xls

If you would rather have the output go to stdout to pipe the output to another
program or to redirect it to a file of your choosing, simply call

    tovcf input.vcf --stdout
