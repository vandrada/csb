# Name
vcfparse.py

# Description
Parses a VCF file and extracts the specified regions.

# Dependencies
## Python Modules
* [PyVCF](https://pypi.python.org/pypi/PyVCF)
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>

# Synopsis

    vcfparse vcf_file [field1 field2 ... fieldN] [-h]

## Arguments
* `vcf_file`: the VCF file to parse
* `fields`: a list of fields to extract from the VCF file.

## Options
* `--help, -h`: print a helpful message and exit.

# Examples
A command such as

    vcfparse test.vcf gq dp sdp ad

will create four separate text files, one for each field. Each text file has a
header of the form

    Chromosome  Position    Value   Sample

which is tab separated and each subsequent line will look something like this

    chr10   181479  27  Sample4


# Thanks
Thanks to the people who have contributed to PyVCF for allowing me to write
_way_ less than one hundred lines of code:)
