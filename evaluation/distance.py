#!/usr/bin/env python

import sys
import argparse
import dendropy

from dendropy.calculate import treecompare

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "original",
        type=argparse.FileType('r'),
        help="File with original trees")
    parser.add_argument(
        "reconstructed",
        type=argparse.FileType('r'),
        help="File with reconstructed trees")
    parser.add_argument(
        "--output", "-o",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Output filename, one tree per input file")
    args = parser.parse_args()

    for t1, t2 in zip(args.original, args.reconstructed):
        tns = dendropy.TaxonNamespace()
        tree1 = dendropy.Tree.get_from_string(
            t1, schema="newick", taxon_namespace=tns)
        tree2 = dendropy.Tree.get_from_string(
            t2, schema="newick", taxon_namespace=tns)
        print(treecompare.euclidean_distance(tree1, tree2))
