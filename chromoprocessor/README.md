# Name
chromoprocessor.py

# Description
Processes multiple BAM files by splitting each BAM file into its regions.
Parallelizes a command similar to

    samtools mpileup 1.bam 2.bam [...] n.bam | java -jar VarScan > out.vcf

The resulting VCF files--one for each region--will be in `vcf/`. In order to
pass arguments to `samtools` and `VarScan` use a `samtools.conf` and
`varscan.conf` file. For more information see Notes below.

# Dependencies
## Python Modules
* [pysam](https://pypi.python.org/pypi/pysam)
* [argparse](https://pypi.python.org/pypi/argparse)

    <sub> \* only if using a Python version &lt; 2.7 </sub>
* [futures](https://pypi.python.org/pypi/futures)

    <sub> \* only if using a Python version &lt; 3.0 </sub>

# Synopsis

    chromoprocessor location action [--file file_name] [--dir dir]
                                    [--list bam [bam ..]] [--n-region]
                                    [--verbose | -v] [-h]

## Arguments
* `location`: the location of the VarScan jar.
* `action`: the action for VarScan to run.

## Options
* `--file`: a file containing the paths to the BAM files to process.
* `--dir`: the path to the directory with the BAM files to process.
* `--list`: a list of the BAM files to process.
* `--n-region`: the number of regions to process in parallel. The default is
two.
* `--verbose`: output additional information.

# Examples
The easiest way to create the file with the name of the BAM files to process is
with `ls`, i.e `ls *.bam > to_process.txt`. Of course, the name of the file is
completely arbitrary and can be anything.

After the file is produced, use the `--file` switch

    chromoprocessor --file to_process.txt /home/You/VarScan.jar mpileup2snp -v

If you want to specify the directory with the BAM files, use the `--dir` switch

    chromoprocessor --dir /path/to/bams/ /home/You/VarScan.jar mpileup2snp -v

Finally, you can also specify a list of BAM files

    chromroprocessor --list /path/to/bam1 /path/to/bam2 /home/You/VarScan.jar mpileup2snp

If you have the hardware and you would like the BAM files to be processed
quicker, you can run more jobs in parallel

    chromoprocessor --dir path/to/bams/ /home/You/VarScan.jar mpileup2snp -v --n-region 6

# Notes
A `varscan.conf` and a `samtools.conf` are expected to be in the current working
directory when the program is called, if they don't exist the default parameters
for VarScan and samtools will be used. The files should contain parameters you
want to pass to VarScan and samtools respectively.

A very minimal example of `samtools.conf` will be

    -d
    1000000

And an example of `varscan.conf` will be

    --output-vcf
    1
    --p-value
    0.2
