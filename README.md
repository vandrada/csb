# Summer 2014 Source Code
## Contents
This is the git repo that contains all code written during the summer of 2014
for the P20 internship.

### Creating VCF Files
* [chromoprocessor/chromoprocessor.py](chromoprocessor/README.md):
processes multiple bam files in parallel
* [tovcf/tovcf.py](tovcf/README.md):
converts an Excel file to a VCF file
* <strike>[parallel/chromosplit.py](parallel/README.md):
processes a _single_ bam file in parallel</strike>

### Processing VCF Files
* [vcfparse/vcfparse.py](vcfparse/README.md):
extracts the specified regions from a VCF file
* [vcfrename/vcfrename.py](vcfrename/README.md):
renames the sample columns in a VCF file

### Graphing
* __graph/__:
this directory contains R scripts written for specific data, they aren't
meant to be general

### Et Cetera
* __install.py__:
installs the Python modules needed for the programs in this repo

__Please note that these links only work when the documentation is local.__

## Installation
Most of the Python programs depend on external libraries and modules. Each
dependency is listed in the `README` for that particular program. However, if
you plan on using all the programs at some point in time, you can run
`install.py` and it will install _all_ the Python modules that
`chromoprocessor`, `vcfparse`, and `tovcf` need for the user.

Note: `install.py` also installs [pip](https://pypi.python.org/pypi/pip)

### For additional information see each program's respective README
