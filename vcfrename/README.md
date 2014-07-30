# Name
vcfrename

# Description
__Dead__ simple program to rename the samples of a VCF file.

# Dependencies
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>

# Synopsis

    vcfrename vcf_file names [-h]

## Arguments
* `vcf_file`: the VCF file to rename
* `names`: a file with the new names

# Examples
To rename the samples of `run.vcf` with the names contained in `names.txt` run

    vcfrename vcf_file names

Each name in `names` should be on a separate line.
