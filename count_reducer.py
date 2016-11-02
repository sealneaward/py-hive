#!/usr/bin/env python

import sys

current_abr = None
current_count = 0
abr = None

for line in sys.stdin:
    abr, count = line.split('\t')
    count = int(count)
    if abr == current_abr:
        current_count += count
    else:
        if current_abr:
            print '%s\t%i' % (current_abr, current_count)
        current_abr = abr
        current_count = count

if current_abr == abr:
    # map current reduced key value pai
    print '%s\t%i' % (current_abr, current_count)
