#!/usr/bin/env python

"""Calculate lingpy-provided tree distances.

Calculate tree distance measures between one or several original and
reconstructed trees using tree comparison methods provided by
Lingpy.

"""

import sys
import argparse
import lingpy.basic.tree

distance_functions = {
    "grf": lambda t1, t2: t1.get_distance(t2, distance='grf'),
    "rf": lambda t1, t2: t1.get_distance(t2, distance='rf'),
    "branch": lambda t1, t2: t1.get_distance(t2, distance='branch'),
    "symmetric": lambda t1, t2: t1.get_distance(t2, distance='symmetric'),
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
        default="grf",
        help="The function to use to calculate the distance between trees. "
        "One of " + ", ".join(distance_functions.keys()))

    args = parser.parse_args()

    for c, (t1, t2) in enumerate(zip(args.original, args.reconstructed)):
        tree1 = lingpy.basic.tree.Tree(t1)
        tree2 = lingpy.basic.tree.Tree(t2)
        print(distance_functions[args.distance](tree1, tree2),
              file=args.output)
    if c == 0:
        # If there was only one original tree, compare it with _each_
        # reconstructed tree.
        for t2 in args.reconstructed:
            tree2 = lingpy.basic.tree.Tree(t2)
            print(distance_functions[args.distance](tree1, tree2),
                  file=args.output)
