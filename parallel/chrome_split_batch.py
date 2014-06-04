#!/usr/bin/env python
"""
Simple script to batch process multiple bam files.

Unfortunately, all files should be indexed and sorted already, only the minumum
of flags (the --verbose flag) are passed to the main program.
"""
import sys
import subprocess
from multiprocessing import Process

processes = []

for bam in sys.argv[1:]:
    p = Process(target=subprocess.call,
                args=(['chrome_split', '-f', bam, '--verbose'], ))
    p.daemon = True
    processes.append(p)

for p in processes:
    p.start()

for p in processes:
    p.join()
