#!/usr/bin/env python

import argparse
import lingpy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Generate random trees
    according to some specification""")

    parser.add_argument(
        '-t', type=int, default=100,
        help="Number of trees to generate")
    parser.add_argument("--taxa", "--languages", "-l", type=str, nargs="+", default=list("ABCDEFGHIJKLMN"),
                        help="Taxon names")
    parser.add_argument('--max', type=int, default=11000,
                        help="Minimum number of change events along a branch")
    parser.add_argument('--min', type=int, default=9000,
                        help="Maximum number of change events along a branch")
    parser.add_argument("--tree-file", default="simulation",
                        help="Filename to write the tree to. "
                        "'-{tree_number:}.tre' is appended automatically. "
                        "Use `--tree-file=-` to output to STDOUT.")

    args = parser.parse_args()

    for i in range(args.t):
        tree = lingpy.basic.tree.random_tree(
            args.taxa, branch_lengths=False)

        if args.tree_file == "-":
            print(tree)
        else:
            with open("{:}-{:d}.tre".format(
                    args.tree_file, i), "w") as tree_file:
                tree_file.write(tree)
