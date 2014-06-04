# Parallel Pipeline
## Summer 2014

### Options and Arguments
#### Arguments
* `-f`, `--file`: the file to process. This should be a .bam file.

#### Options
* `--index`: if the bam file has not been indexed this flag should be passed.

* `--sort`: if the bam file has not been sorted this flag should be passed.
This switch implies `--index`

* `-v`, `--verbose`: if this flag is passed, additional information will be
printed out while the program is running.

### Notes
* The program was rewritten using the `multiprocessing` module instead of the
`threading` module because processes are cheaper on Linux and OS X than threads.
On Windows, the inverse is true.

* The program creates two directories in your working directory with the
suffixes of `bam_` and `mpileup_`, the suffix of each will be the name of the
passed in file. i.e `chrome_split -f test.bam` will create `bam_test/` and
`mpileup_test/`.
