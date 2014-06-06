# Name
Parallel Region Analyzer

# Description
Processes a bam file by spawning a process to handle each region in the bam
file. Each process creates a new bam file for that process, creates a mpileup
file, and finally creates a vcf file. The arguments to pass to VarScan are read
from a `varscan.conf` file. This file is expected to be in the current working
directory.

# Dependencies and Preliminaries
* pysam: install with `pip install pysam`.
* samtools: install from [SourceForge](http://samtools.sourceforge.net/) or with
Homebrew.
* VarScan: install from [SourceForge](http://varscan.sourceforge.net/).
* vcftools: install from [SourceForge](http://vcftools.sourceforge.net/) or with
Homebrew.

# Synopsis
usage: chrome_split --file=[your file] --varscan=[VarScan.jar]
--action=[VarScan action]

## Arguments
* `-f`, `--file`: the bam file to process.
* `--varscan`: the location to the VarScan jar.
* `--action`: the action for VarScan to run.

## Options
### Options related to bam files
* `--index`: if the bam file has not been indexed this flag should be passed.

* `--sort`: if the bam file has not been sorted this flag should be passed.
This switch implies `--index`.

### Options related to VarScan
* `--varscan-conf`: the location of `varscan.conf` if one is not in the current
working directory.

### Options related to this program
* `--keep-bam`: keeps the bam files for each region. The default behavior is
to remove the bam file once the mpileup file has been created.

* `--keep-mpileup`: keeps the mpileup files for each region. The default
behavior is to remove them once the vcf file has been created.

* `--keep-all`: keeps the bam file and the mpileup files. Implies `--keep-bam`
and `--keep-mpileup`.

* `-v`, `--verbose`: if this flag is passed, additional information will be
printed out while the program is running.

# Examples
The most basic usage is:

    chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar --action=mpileup2snp

This command will run `mpileup2snp` on the regions of `your.bam`.
Alternatively you can specify the file with `-f` instead of `--file=`

    chrome_split -f your.bam --varscan=/Users/You/VarScan.jar --action=mpileup2snp --verbose

This command will run `mpileup2snp` on the regions of `your.bam` and print
additional information as each step completes.

If you would like to keep some of the intermediate files, this example shows how
to keep the bam files created.

    chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar --action=mpileup2snp --keep-bam

This command will run `mpileup2snp` on the regions of `your.bam` and will keep
the intermediate bam files that are created in the process.

Finally, if there isn't a `varscan.conf` in your working directory, you need to
pass the absolute path to a `varscan.conf`

    chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar --action=mpileup2snp --varscan-conf=/Users/You/varscan.conf

# Notes
* The program creates three directories in your working directory with the
prefixes of `bam_`, `mpileup_`, and `vcf_` the suffix of each will be the name
of the passed in file. i.e `chrome_split -f test.bam` will create `bam_test/`,
`mpileup_test/`, and `vcf_test/`.

* To save space, the default behavior is to delete each file once it has been
processed. For small bam files the three directories shouldn't be a problem, but
processing an initial bam file of five gigabytes in size produced an additional
forty gigabytes. If you would like to keep the bam file pass `--keep-bam`; if
you would like to keep the mpileup files pass `--keep-mpileup`; finally, if you
would like to keep all the files pass `--keep-all`
