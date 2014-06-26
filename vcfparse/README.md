# Name
vcfparse

# Description
Parses a vcf file and extracts the specified regions.

# Dependencies
## Python Modules
* [PyVCF](https://github.com/jamescasbon/PyVCF)

# Synopsis
vcfparse vcf_file --fields [...] [-h] [--pretty]

## Arguments
* `vcf_file`: the vcf file to parse
* `--fields`: the fields to extract from the vcf file.

## Options
* `--pretty`: prints a header

# Examples
    vcfparse test.vcf --fields gq dp sdp ad

Will print out the value for the GQ, DP, SDP, and AD fields from test.vcf with
output similar to this:

    34 27 27 2                     60 41 41 17


    255 259 260 170                255 175 175 111
                                   41 14 14 10
                                   6 15 15 5

While

    vcfparse test.vcf --fields gq dp sdp ad --pretty

will produce output similar to this

                    Sample1                         Sample2
                    GQ DP SDP AD                    GQ DP SDP AD
    chr10:181479     34 27 27 2                     60 41 41 17
    chr10:649857
    chr10:649859
    chr10:1034412    255 259 260 170                255 175 175 111
    chr10:1041487                                   41 14 14 10
    chr10:1056169                                   6 15 15 5

# Thanks
Thanks to the people who have contributed to PyVCF for allowing me to write less
than one hundred lines of code:)
