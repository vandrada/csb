# Parallel Pipeline
## Summer 2014
### Description
Processes a bam file by spawning a process to handle each region in the bam
file. Each process creates a new bam file for that process, creates a mpileup
file, and finally creates a vcf file. The arguments to pass to VarScan are read
from a `varscan.conf` file. This file is expected to be in the current working
directory.

### Options and Arguments
#### Needed Arguments
* `-f`, `--file`: the bam file to process.
* `--varscan`: the location to the VarScan jar
* `--action`: the action for VarScan to run

#### Options
* `--index`: if the bam file has not been indexed this flag should be passed.

* `--sort`: if the bam file has not been sorted this flag should be passed.
This switch implies `--index`

* `--varscan-conf`: the location of `varscan.conf` if one is not in the current
working directory

* `--keep-bam`: keeps the bam files for each region. The default behavior is
to remove the bam file once the mpileup file has been created.

* `--keep-mpileup`: keeps the mpileup files for each region. The default
behavior is to remove them once the vcf file has been created.

* `-v`, `--verbose`: if this flag is passed, additional information will be
printed out while the program is running.

#### Examples
* `chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar
--action=mpileup2snp`: This command will run `mpileup2snp` on `your.bam`

* `chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar
--action=mpileup2snp --verbose`: This command will run `mpileup2snp` on
`your.bam` and print additional information as each step completes.

* `chrome_split --file=your.bam --varscan=/Users/You/VarScan.jar
--action=mpileup2snp --keep-bam`: This command will run `mpileup2snp` on
`your.bam` and will keep the intermediate bam files that are created in the
process.

### Notes
* The program creates three directories in your working directory with the
suffixes of `bam_`, `mpileup_`, and `vcf_` the suffix of each will be the name
of the passed in file. i.e `chrome_split -f test.bam` will create `bam_test/`,
`mpileup_test/`, and `vcf_test/`.

* To save space, the default behavior is to delete each file once it has been
processed. For small files the three directories shouldn't be a problem, but
processing an initial bam file of five gigabytes in size produced an additional
forty gigabytes. If you would like to keep the bam file pass `--keep-bam`; if
you would like to keep the mpileup files pass `--keep-mpileup`.
