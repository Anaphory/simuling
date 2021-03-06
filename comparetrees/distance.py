#!/usr/bin/env python

"""Calculate dendropy-provided tree distances.

Calculate tree distance measures between one or several original and
reconstructed trees using tree comparison methods provided by
dendropy.

"""

import sys
import argparse
import dendropy

from dendropy.calculate import treecompare

distance_functions = {
    "euclidean": treecompare.euclidean_distance,
    "bipartition": lambda t1, t2: sum(
        treecompare.false_positives_and_negatives(t1, t2)),
    "wrf": treecompare.weighted_robinson_foulds_distance,
    "weighted_robinson_foulds": treecompare.weighted_robinson_foulds_distance,
    "rf": treecompare.unweighted_robinson_foulds_distance,
    "unweighted_robinson_foulds":
        treecompare.unweighted_robinson_foulds_distance,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
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
    parser.add_argument(
        "--distance",
        choices=distance_functions.keys(),
        default="rf",
        help="The function to use to calculate the distance between trees. "
        "One of " + ", ".join(distance_functions.keys()))

    args = parser.parse_args()

    for c, (t1, t2) in enumerate(zip(args.original, args.reconstructed)):
        tns = dendropy.TaxonNamespace()
        tree1 = dendropy.Tree.get_from_string(
            t1, schema="newick", taxon_namespace=tns)
        tree2 = dendropy.Tree.get_from_string(
            t2, schema="newick", taxon_namespace=tns)
        print(distance_functions[args.distance](tree1, tree2),
              file=args.output)
    if c == 0:
        # If there was only one original tree, compare it with _each_
        # reconstructed tree.
        for t2 in args.reconstructed:
            tree2 = dendropy.Tree.get_from_string(
                t2, schema="newick", taxon_namespace=tns)
            print(distance_functions[args.distance](tree1, tree2),
                  file=args.output)
