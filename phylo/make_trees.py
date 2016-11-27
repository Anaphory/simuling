#!/usr/bin/env python

import argparse
import newick
import random


def random_tree(taxa, branch_length=lambda: random.random()):
    """Generate a random tree typology

    This is a re-implementation of the random tree generator from
    lingpy.

    """
    taxa_list = [t for t in taxa]
    random.shuffle(taxa_list)

    clades = []
    for taxon in taxa_list:
        clades.append(
            newick.Node(str(taxon),
                        length = str(branch_length())))
    while len(clades) > 1:
        ulti_elem = clades.pop()
        penulti_elem = clades.pop()
        clades.insert(
            0,
            newick.Node.create(
                length=str(branch_length()),
                descendants=[ulti_elem, penulti_elem]))
        random.shuffle(clades)
    return clades[0]



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Generate random trees
    according to some specification""")

    parser.add_argument(
        '-t', type=int, default=100,
        help="Number of trees to generate")
    parser.add_argument("--taxa", "--languages", "-l", type=str,
                        nargs="+", default=list("ABCDEFGHIJKLMN"),
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
        tree = random_tree(
            args.taxa, branch_length=lambda: 1)

        if args.tree_file == "-":
            print(tree.newick)
        else:
            with open("{:}-{:d}.tre".format(
                    args.tree_file, i), "w") as tree_file:
                newick.dump(tree, tree_file)
