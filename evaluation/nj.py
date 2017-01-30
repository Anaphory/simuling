#!/usr/bin/env python

"""Build a neighbor joining tree from a CLDF file.

From a csv file mapping (Language_ID, Feature_ID) pairs to values,
construct a tree using the neighbor joining algorithm.

"""

import sys
import pandas
import argparse

from Bio.Phylo.TreeConstruction import _DistanceMatrix
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor
from Bio.Phylo.NewickIO import Writer

def nj_wordlist(wordlist):
    wordlist = pandas.read_csv(wordlist, sep="\t")
    cogids = []
    languages = []
    for language, data in wordlist.groupby("Language_ID"):
        languages.append(language)
        cogids.append(set(data["Concept_CogID"]))

    dm = _DistanceMatrix(
        languages,
        [[len(cogids[i] ^ cogids[j])
        for j in range(i + 1)]
        for i in range(len(cogids))])

    constructor = DistanceTreeConstructor()
    tree = constructor.nj(dm)
    return tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "wordlist", nargs="+",
        type=argparse.FileType('r'),
        help="The word list input files")
    parser.add_argument(
        "--output", "-o",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Output filename, one tree per input file")
    args = parser.parse_args()

    trees = []
    for wordlist in args.wordlist:
        trees.append(nj_wordlist(wordlist))
    
    Writer(trees).write(args.output)
