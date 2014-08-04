# Name
chromoprocessor.py

# Description
Processes multiple BAM files by splitting each BAM file into its regions.
Parallelizes a command similar to

    samtools mpileup 1.bam 2.bam [...] n.bam | java -jar VarScan > out.vcf

The resulting VCF files--one for each region--will be in `vcf/`.

# Dependencies
## Python Modules
* [pysam](https://pypi.python.org/pypi/pysam)
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>
* [futures](https://pypi.python.org/pypi/futures)

    <sub> \* only if using a Python version &lt; 3.0 </sub>

# Synopsis

    chromoprocessor file_names location action [-h] [--n-region] [--verbose | -v]

## Arguments
* `file_names`: a file containing the names of the BAM files to process.
* `location`: the location of the VarScan jar.
* `action`: the action for VarScan to run.

## Options
* `--n-region`: the number of regions to process in parallel. The default is
two.
* `--verbose`: output additional information.

# Examples
The easiest way to create the file with the name of the BAM files to process is
with `ls`, i.e `ls *.bam > to_process.txt`. Of course, the name of the file is
completely arbitrary and can be anything.

After the file is produced it's as simple as

    chromoprocessor to_process.txt /home/You/VarScan.jar mpileup2snp -v

If you have the hardware and you would like the BAM files to be processed
quicker, you can run more jobs in parallel

    chromoprocessor to_process.txt /home/You/VarScan.jar mpileup2snp -v --n-region=6

# Notes
A `varscan.conf` and a `samtools.conf` are expected to be in the current
working directory when the program is called. The files should contain the
arguments and parameters you want to pass to VarScan and samtools respectively.

A very minimal example of `samtools.conf` will be

    -d
    1000000

And an example of `varscan.conf` will be

    --output-vcf
    1
    --p-value
    0.2
