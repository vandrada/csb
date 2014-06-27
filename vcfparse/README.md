# Name
vcfparse

# Description
Parses a vcf file and extracts the specified regions.

# Dependencies
## Python Modules
* [PyVCF](https://github.com/jamescasbon/PyVCF)

# Synopsis
vcfparse vcf_file [field1 field2 ... fieldN] [-h]

## Arguments
* `vcf_file`: the vcf file to parse
* `fields`: a list of fields to extract from the vcf file.

## Options
* `--help, -h`: print a helpful message and exit.

# Examples
A command such as

    vcfparse test.vcf gq dp sdp ad

will create four separate text files, one for each field. Each text file has a
header of the form

    Chromosome  Position    Sample1 [...]   SampleN

which is tab separated and each subsequent line will look something like this

    chr10   181479  27      41


# Thanks
Thanks to the people who have contributed to PyVCF for allowing me to write
_way_ less than one hundred lines of code:)
