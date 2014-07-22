# Summer 2014 Source Code
## Contents
This is the git repo that contains all code written during the summer of 2014
for the P20 internship.

The following directories/files are included:

* [chromoprocessor/chromoprocessor.py](../chromoprocessor/doc/README.html):
processes _multiple_ bam files in parallel.
* [vcfparse/vcfparse.py](../vcfparse/doc/README.html):
extracts the specified regions from a VCF file
* [tovcf/tovcf.py](../tovcf/doc/README.html):
converts an Excel file to a VCF file
* __graph/__:
this directory contains R scripts written for specific data, they aren't
meant to be general.
* __install.py__:
installs the Python modules needed for the programs in this repo.
* [parallel/chromosplit.py](../parallel/doc/README.html): __deprecated__
<strike>processes a _single_ bam file in parallel.</strike>

## Clarification
While `chromoprocessor` and `chromosplit` appear to be very similar, they are in
fact very different from each other.

`chromoprocessor` is the _correct_ program for processing multiple BAM files in
parallel. Effectively, it parallelizes a command similar to

    samtools mpileup file1.bam file2.bam [...] | java -jar Varscan mpileup2snp

`chromosplit` processes a _single_ BAM file by splitting it into regions and
processing each region on it's own. `chromosplit` parallelizes a command similar
to

    samtools mpileup file.bam | java -jar Varscan mpileup2snp

However, `chromoprocessor` is just as capable of processing a single BAM file,
because of this `chromosplit` is deprecated. With a single BAM file to process
the pipeline that `chromoprocessor` implements is equivalent to the one that
`chromosplit` implemented.

## Installation
Most of the Python programs depend on external libraries and modules. Each
dependency is listed in the `README` for that particular program. However, if
you plan on using all the programs at some point in time, you can run
`install.py` and it will install _all_ the Python modules that
`chromoprocessor`, `vcfparse`, and `tovcf` need for the user.

Note: `install.py` also installs [pip](https://pypi.python.org/pypi/pip)

### For additional information see each program's respective README
