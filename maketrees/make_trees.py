#!/usr/bin/env python

import argparse
import bisect
import random
import newick


def create_random_tree(size, length=random.random()):
    """Generate a random tree.

    This builds a random tree with a given branch length
    distribution, and roughly balanced node heights.

    """
    nodes = []
    for taxon in range(size):
        nodes.append(newick.Node(
            name=taxon,
            length=length(),
            length_parser=float,
            length_formatter="{:f}".format))

    nodes.sort(key=lambda x: x.length)
    heights = [node.length for node in nodes]
    while len(nodes) > 1:
        # Take the two lowest nodes
        node0 = nodes[0]
        node1 = nodes[1]
        # Keep the rest
        nodes = nodes[2:]
        heights = heights[2:]
        # Stick a new node on top of those lowest nodes
        new_branch_length = length()
        height = (heights[0] + heights[1]) / 2 + new_branch_length
        tree = newick.Node(
            length = new_branch_length,
            length.parser=float,
            length_formatter="{:f}".format)
        tree.add_descendant(node0)
        tree.add_descendant(node1)
        # Put the new subtree in the right place in height order
        i = bisect.bisect(heights, height)
        heights.insert(i, height)
        nodes.insert(i, tree)
    return nodes[0]


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
                        length=str(branch_length())))
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
    parser.add_argument('--max', type=int, default=1100,
                        help="Minimum number of change events along a branch")
    parser.add_argument('--min', type=int, default=900,
                        help="Maximum number of change events along a branch")
    parser.add_argument("--tree-file", default="simulation.tre",
                        type=argparse.FileType('w'),
                        help="Filename to write the tree to. "
                        "Use `--tree-file=-` to output to STDOUT.")

    args = parser.parse_args()

    for i in range(args.t):
        tree = create_random_tree(
            args.taxa, branch_length=lambda:
            random.random()*(args.max-args.min)+args.min)

        args.tree_file.write(
            tree.newick)
        args.tree_file.write("\n")
