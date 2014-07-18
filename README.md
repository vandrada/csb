# Summer 2014 Source Code
## Contents
This is the git repo that contains all code written during the summer of 2014
for the P20 internship.

The following programs are included:

* __chromoprocessor__: processes _multiple_ bam files in parallel
* __vcfparse__: extracts the specified regions from a VCF file
* __tovcf__: converts an Excel file to a VCF file
* __graph__: this directory contains R scripts written for specific data, they
aren't meant to be general.
* __chromosplit__: processes a _single_ bam file in parallel

## Clarification
While `chromoprocessor` and `chromosplit` appear to be very similar, they are in
fact very different from each other.

`chromoprocessor` is the _correct_ program for processing multiple BAM files in
parallel. Effectiviely, it parallelizes a command similar to

    samtools mpileup file1.bam file2.bam [...] | java -jar Varscan mpileup2snp

`chromosplit` processes a _single_ BAM file by splitting it into regions and
processing each region on it's own. `chromosplit` parallelizes a command similar
to

    samtools mpileup file.bam | java -jar Varscan mpileup2snp

## Installation
Most of the Python programs depend on external libraries and modules. Each
dependency is listed in the `README` for that particular program. However, if
you plan on using all the programs at some point in time, you can run
`install.py` and it will install _all_ the Python modules that
`chromoprocessor`, `vcfparse`, and `tovcf` need. Note that they will be
installed for the user only.

### For additional information see each program's respective README
