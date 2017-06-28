#!/usr/bin/env python

"""Command line tool for a complete tree→word lists→trees toolchain.

Create simulated word lists from a tree, and then try to reconstruct
trees from the word list using various available methods.

"""

import itertools
import argparse
import lingpy


def reconstruct_random(wordlist):
    """Pseudo-Reconstruction by just drawing a random tree.

    This is useful for comparison, because this is the dumbest
    'reconstruction' method possible.

    """
    return lingpy.basic.tree.Tree(lingpy.basic.tree.random_tree(wl.taxa))


def reconstruct_neighbor(wordlist):
    """Construct a tree using neighbor-joining."""
    wordlist.calculate('tree', ref='cogid', tree_calc='neighbor')
    return wordlist.tree


def reconstruct_upgma(wordlist):
    """Construct a tree using UPGMA clustering."""
    wordlist.calculate('tree', ref='cogid')
    return lingpy.upgma(wordlist.distances, wordlist.taxa)


parser = argparse.ArgumentParser(
    description="""Take some word lists and use computational methods to create
    trees from them.""",
    epilog="""Examples:

        $ %(prog)s simulation-b200-*.tsv --real-tree simulation-*.tre --nn

    to average the quality of NN trees over multiple simulations, each
    with the same word list sampler.

        $ %(prog)s simulation-b*-0.tsv --real-tree simulation-0.tre --upgma

    to average the quality of UPGMA trees over word list samples with
    various list sizes, each generated from the same simulated
    language phylogeny.

    """)
parser.add_argument("wordlists", nargs="+", help="Lingpy wordlist tsv file")
parser.add_argument(
    "--real-tree", nargs="+",
    help="Either a list of Newick strings of the reference tree, or a list of "
    "filenames, each containing areference tree in Newick format.")
parser.add_argument(
    "--random", action="store_const", const=reconstruct_random, dest="method",
    help="Instead of reconstructing, draw random trees with the right set of "
    "taxa for comparison")
parser.add_argument(
    "--nn", action="store_const", const=reconstruct_neighbor, dest="method",
    help="Use Nearest Neighbor Joining to reconstruct trees")
parser.add_argument(
    "--upgma", action="store_const", const=reconstruct_upgma, dest="method",
    help="Use the Unweighted Pair Group Method with Arithmetic Mean (UPGMA) "
    "to reconstruct trees")
args = parser.parse_args()


if args.real_tree:
    try:
        real_tree = [lingpy.basic.tree.Tree(
            newick_string) for newick_string in args.real_tree]
    except lingpy.thirdparty.cogent.newick.TreeParseError:
        real_tree = [lingpy.basic.tree.Tree(
            open(filename).read()) for filename in args.real_tree]
else:
    real_tree = [None]


distances = []
for wordlist, real_tree in zip(args.wordlists, itertools.cycle(real_tree)):
    wl = lingpy.Wordlist(wordlist)
    tree = args.method(wl)
    print(tree)
    if real_tree:
        d = real_tree.get_distance(tree)
        distances.append(d)
        print("Word list {:s} distance to real tree: {:.3f}".format(
            wordlist,
            d))


if args.real_tree:
    print("Average distance to real tree: {:.3f}".format(
        sum(distances) / len(distances)))
