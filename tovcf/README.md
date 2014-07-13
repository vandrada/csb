# Name
tovcf

# Description
Transfroms a csv file to a VCF file.

# Dependencies
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>

# Synopsis
usage:

    tovcf file.csv [-h] [--out output.vcf]

## Arguments
* `file.csv`: the Excel file converted to a csv file.

## Options
* `--out`: the output file to write to. The default is stdout.

# Examples
To write the VCF file to stdout simply call

    tovcf input.vcf

If you want to specify the file to write to, simply call

    tovcf input.vcf --out out.vcf

# Notes
Since the default behavior is to write to stdout you can also pipe the output to
another program or redirect it to a file manually.
