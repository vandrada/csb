# ** DEPRECATED **

# Name
Parallel Region Analyzer

# Description
Processes a BAM file by spawning a process to handle each region in the BAM
file. Each process creates a new BAM file for that region, creates a mpileup
file, and finally creates a vcf file. The workflow can be pictured like this:

__region -> [samtools mpileup] -> [VarScan]__

The vcf files are then merged into one file that is located in `vcf_*/` with the
name of the passed in BAM file.  The arguments to pass to VarScan are read from
a `varscan.conf` file and the arguments to pass to samtools are read from a
`samtools.conf` file. This file is expected to be in the current working
directory.

# Dependencies and Preliminaries
## Python Libraries
* pysam: install with `pip install pysam`.
* futures: install with `pip install futures`.

  <sub> \* only if using a Python version &lt; 3 \* </sub>
* argparse: install with `pip install argparse`.

  <sub> \* only if using a Python version &lt; 2.7 \* </sub>
## Other Software
* samtools: install from [SourceForge](http://samtools.sourceforge.net/) or with
Homebrew if using OS X.
* vcftools: install from [SourceForge](http://vcftools.sourceforge.net/) or with
Homebrew if using OS X. Be sure to export the `PERL5LIB` variable.
* VarScan: install from [SourceForge](http://varscan.sourceforge.net/).

# Synopsis

    chromo_split infile action varscan_location

## Arguments
* `infile`: the path of the BAM file to process.
* `action`: the action for VarScan to run.
* `varscan_location`: the path to the VarScan jar.

## Options
### Options Related to the BAM File
* `--index`: if the BAM file has not been indexed this flag should be passed.

* `--sort`: if the BAM file has not been sorted this flag should be passed.
This switch implies `--index`.

### Options Related to Configuration Files
* `--varscan-conf`: the location of `varscan.conf` if one is _not_ in the
current working directory.

* `--samtools-conf`: the location of `samtools.conf` if one is _not_ in the
current working directory

### Other Options
* `--with-pipe`: instead of writing the intermediate files to disk, the commands
are piped into each other, avoiding disk IO. The directories for BAM files and
mpileup files are not created. Equivalent to

        samtools mpileup test.bam | java -jar Varscan.jar

* `--n-procs`: the total number of concurrent processes to run at a time. The
default is two processes.

* `--keep-bam`: keeps the BAM files for each region. The default behavior is
to remove the BAM file once the mpileup file has been created.

* `--keep-mpileup`: keeps the mpileup files for each region. The default
behavior is to remove them once the vcf file has been created.

* `--keep-all`: keeps the BAM file and the mpileup files. Implies `--keep-bam`
and `--keep-mpileup`.

* `-v`, `--verbose`: if this flag is passed, additional information will be
printed out while the program is running.

# Examples
The most basic usage is:

    chromo_split your.bam mpileup2snp VarScan.jar

This command will run `mpileup2snp` on the regions of `your.bam`, processing two
regions in parallel.

There is also a `--verbose` flag.

    chromo_split your.bam mpileup2snp VarScan.jar --verbose

This command will run `mpileup2snp` on the regions of `your.bam` and print
additional information as each step completes. You can also specify `--verbose`
with `-v`.

If you would like to keep some of the intermediate files, this example shows how
to keep the BAM files created.

    chromo_split your.bam mpileup2snp VarScan.jar --keep-bam

This command will run `mpileup2snp` on the regions of `your.bam` and will keep
the intermediate BAM files that are created in the process.

If you want the program to run a little faster, this example shows how to avoid
disk IO.

    chromo_split your.bam mpileup2snp VarScan.jar --with-pipe

If you want the number of processes to be limited to one, you can run the
program like this:

    chromo_split your.bam mpileup2snp VarScan.jar --n-procs=1

Finally, if there isn't a `varscan.conf` in your working directory, you need to
pass the path to a `varscan.conf`

    chromo_split your.bam mpileup2snp VarScan.jar --varscan-conf=/home/You/varscan.conf

# Notes
* The program creates three directories in your working directory with the
prefixes of `bam_`, `mpileup_`, and `vcf_` the suffix of each will be the name
of the passed in file. i.e `chromo_split test.bam [...]` will create
`bam_test/`, `mpileup_test/`, and `vcf_test/`.

* To save space, the default behavior is to delete each file once it has been
processed. For small BAM files the three directories shouldn't be a problem, but
processing a bigger BAM file can produce a lot of additional data. If you would
like to keep the BAM file pass `--keep-bam`; if you would like to keep the
mpileup files pass `--keep-mpileup`; finally, if you would like to keep all the
files pass `--keep-all`. The vcf files are _always_ kept.

* The `varscan.conf` and `samtools.conf` files are simply files where each
argument and switch to pass to VarScan or samtools are on a single line. To see
examples of these files look [here](../chromoprocessor/README.md)
