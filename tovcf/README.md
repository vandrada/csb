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

    tovcf file.xls [-h] [--out output.vcf]

## Arguments
* `file.xls`: the Excel file to convert to a VCF file. xlsx files are also
supported.

## Options
* `--out`: the output file to write to. The default is stdout.

# Examples
To write the VCF file to stdout simply call

    tovcf input.xls

If you want to specify the file to write to, simply call

    tovcf input.vcf --out out.vcf

# Notes
* Since the default behavior is to write to stdout you can also pipe the output to
another program or redirect it to a file manually.
