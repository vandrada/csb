"""
Simple script to batch process multiple bam files.
"""
import sys

to_process = sys.argv[1:]

for bam in to_process:
    subprocess.call(['chrome_split.py', '-f', bam])
