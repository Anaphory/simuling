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


def nj_wordlist(
        wordlist,
        column="Value",
        method=DistanceTreeConstructor.nj):
    """Create a tree using Hamming distances.

    From the CLDF Dataframe `wordlist`, create a tree using a distance
    method (neighbor joining, the default, or UPGMA) based on the
    Hamming distance (size of the symmetric difference) of
    presence/absence of the set of values in `column`.

    """
    wordlist = pandas.read_csv(wordlist, sep="\t")
    cogids = []
    languages = []
    for language, data in wordlist.groupby("Language_ID"):
        languages.append(language)
        cogids.append(set(data[column]))

    dm = _DistanceMatrix(languages, [
        [len(cogids[i] ^ cogids[j])
         for j in range(i + 1)]
        for i in range(len(cogids))])

    constructor = DistanceTreeConstructor()
    tree = method(constructor, dm)
    return tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Apply distance-based tree building methods "
        "to word list data")
    parser.add_argument(
        "wordlist", nargs="+",
        type=argparse.FileType('r'),
        help="The word list input files")
    parser.add_argument(
        "--output", "-o",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Output filename, one tree per input file")
    parser.add_argument(
        "--value-column",
        default="Concept_CogID",
        help="The column to calculate the Hamming distances on")
    parser.add_argument(
        "--upgma",
        default=DistanceTreeConstructor.nj,
        dest="method",
        action="store_const", const=DistanceTreeConstructor.upgma,
        help="Use UPGMA instead of NJ to construct the tree")
        
    args = parser.parse_args()

    trees = []
    for wordlist in args.wordlist:
        trees.append(nj_wordlist(wordlist, args.value_column))

    Writer(trees).write(args.output)
