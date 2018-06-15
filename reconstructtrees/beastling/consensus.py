#!/usr/bin/env python

"""Construct a consensus tree."""

import sys
from Bio import Phylo
from Bio.Phylo.Consensus import majority_consensus as consensus
# Or: strict_ or majority_ or adam_

if __name__ == "__main__":
    tree = consensus(list(Phylo.parse(sys.argv[1], 'nexus')))
    for i in Phylo.NewickIO.Writer([tree]).to_strings():
        print(i)
