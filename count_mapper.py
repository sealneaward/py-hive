#!/usr/bin/env python

import sys

for line in sys.stdin:
    line = line.decode('utf-8')
    team_abr = line[3]
    # map key value pair of team abbreviation and intermediate count
    print "%s\t%i" % (team_abr, 1)
