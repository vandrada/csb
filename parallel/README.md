# Name
Parallel Region Analyzer

# Description
Processes a bam file by spawning a process to handle each region in the bam
file. Each process creates a new bam file for that region, creates a mpileup
file, and finally creates a vcf file. The vcf files are then merged into one
file that is located in `vcf_dir/` with the name of the passed in bam file.  The
arguments to pass to VarScan are read from a `varscan.conf` file. This file is
expected to be in the current working directory.

# Dependencies and Preliminaries
* pysam: install with `pip install pysam`.
* futures: install with `pip install futures`.
* samtools: install from [SourceForge](http://samtools.sourceforge.net/) or with
Homebrew.
* VarScan: install from [SourceForge](http://varscan.sourceforge.net/).
* vcftools: install from [SourceForge](http://vcftools.sourceforge.net/) or with
Homebrew. Be sure to export `PERL5LIB`.

# Synopsis
usage: chromo\_split infile action varscan\_location

## Arguments
* `infile`: the bam file to process.
* `action`: the action for VarScan to run.
* `varscan_location`: the location to the VarScan jar.

## Options
### Options Related to  the bam File
* `--index`: if the bam file has not been indexed this flag should be passed.

* `--sort`: if the bam file has not been sorted this flag should be passed.
This switch implies `--index`.

### Options Related to VarScan
* `--varscan-conf`: the location of `varscan.conf` if one is not in the current
working directory.

### Other Options
* `--with-pipe`: instead of writing the intermediate files to disk, the commands
are piped into each other, avoiding disk IO. A directory for bam files and
mpileup files are not created.

* `--n-procs`: the total number of concurrent processes to run at a time. The
default is the total number of processes.

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

    chromo_split your.bam mpileup2snp /Users/You/VarScan.jar

This command will run `mpileup2snp` on the regions of `your.bam`.

There is also a `--verbose` flag.

    chromo_split your.bam /mpileup2snp Users/You/VarScan.jar --verbose

This command will run `mpileup2snp` on the regions of `your.bam` and print
additional information as each step completes. You can also specify `--verbose`
with `-v`.

If you would like to keep some of the intermediate files, this example shows how
to keep the bam files created.

    chromo_split your.bam mpileup2snp /Users/You/VarScan.jar --keep-bam

This command will run `mpileup2snp` on the regions of `your.bam` and will keep
the intermediate bam files that are created in the process.

If you want the program to run a little faster, this example shows how to avoid
disk IO.

    chromo_split your.bam mpileup2snp /Users/Your/VarScan.jar --with-pipe

Finally, if there isn't a `varscan.conf` in your working directory, you need to
pass the absolute path to a `varscan.conf`

    chromo_split your.bam mpileup2snp /Users/You/VarScan.jar --varscan-conf=/Users/You/varscan.conf

# Notes
* The program creates three directories in your working directory with the
prefixes of `bam_`, `mpileup_`, and `vcf_` the suffix of each will be the name
of the passed in file. i.e `chromo_split test.bam [...]` will create
`bam_test/`, `mpileup_test/`, and `vcf_test/`.

* To save space, the default behavior is to delete each file once it has been
processed. For small bam files the three directories shouldn't be a problem, but
processing a bigger bam file can produce a lot of additional data. If you would
like to keep the bam file pass `--keep-bam`; if you would like to keep the
mpileup files pass `--keep-mpileup`; finally, if you would like to keep all the
files pass `--keep-all`. The vcf files are _always_ kept.

* The `varscan.conf` file is simply a file where each argument to pass to
VarScan is on a single line.
