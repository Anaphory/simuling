#!/usr/bin/env python

import networkx
import json
import sys

if __name__=="__main__":
    options = json.load(open(sys.argv[1]))
    with open("Data/output", "w") as output:
        print(options, file=output)
