#!/usr/bin/env python


"""Run a language evolution model.

This module implements the CLI interface for running a very simple
forward-time phylogenetic simulation of cognate class evolution in a
language family represented by a given tree.

"""

from collections import defaultdict
import argparse
import random
import csv
import networkx
import newick


from .phylo import Phylogeny
from .language import Language


parser = argparse.ArgumentParser(description=""" Run a very simple forward-time
phylogenetic simulation of cognate class evolution in a language
family.""")

group = parser.add_argument_group("Shared properties of the languages")
group.add_argument("--concepts", '-s', type=int, default=2000,
                   help="Number of concepts to be simulated")
group.add_argument("--fields", '-f', type=int, default=50,
                   help="Number of semantic fields the concepts show")
group.add_argument("--semantic-network", type=argparse.FileType('r'),
                   help="File containing the semantic network to be used (eg. "
                   "a colexification graph) in GLM format")
group = parser.add_argument_group("Properties of the phylogenetic simulation")
group.add_argument("trees", type=argparse.FileType("r"), nargs="+",
                   help="""Files containing Newick trees (one tree per line) to be
                   simulated. You can specify the same tree file
                   multiple times to obtain multiple simulations.""")
group.add_argument("--scale", type=float, default=1,
                   help="""Scaling factor of the tree, or equivalently the number of change
                   events per unit of branchlength.""")
group.add_argument('--p-loss', type=float, default=0.5,
                   help="Probability, per time step, that a word becomes "
                   "less likely for a meaning")
group.add_argument('--p-gain', type=float, default=0.4,
                   help="Probability, per time step, that a word gains a "
                   "related meaning")
group.add_argument('--p-new', type=float, default=0.1,
                   help="Probability, per time step, that a new word arises")
group.add_argument(
    '--wordlist', type=str, default="{tree}-{i}.tsv",
    help="""Filename to write the word lists to.  You can use the placeholders
    {tree} to get the corresponding tree file base name (without
    `.tsv`), and {i} for the number of the simulation (starting at `1`
    for the first simulation).""")
group.add_argument(
    "--sample-internal-nodes", action="store_true", default=False,
    help="Sample word lists also from the tree's internal nodes")


args = parser.parse_args()


if args.semantic_network:
    related_concepts = networkx.parse_gml(args.semantic_network)
else:
    concept2field = defaultdict(set)
    for c in range(args.concepts):
        concept2field[random.randint(0, args.fields - 1)].add(c)
    related_concepts = {}
    for field in concept2field.values():
        for concept in field:
            related_concepts[concept] = field - {concept}

i = 0
for _, tree_file in enumerate(args.trees):
    for tree in newick.load(tree_file):
        i += 1

        phy = Phylogeny(
            related_concepts,
            basic=[],
            tree=tree,
            scale=args.scale)

        phy.simulate(
            p_loss=args.p_loss,
            p_gain=args.p_gain,
            p_new=args.p_new)

        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining

        dataframe, columns = phy.collect_word_list(
            Language.vocabulary,
            collect_tips_only=not args.sample_internal_nodes)
        filename = args.wordlist.format(
            tree=tree_file.name[:-4]
            if tree_file.name.endswith(".tre")
            else tree_file,
            i=i)
        with open(filename, "w") as wordlist_file:
            writer = csv.writer(wordlist_file, 'excel-tab')
            writer.writerow(columns)
            writer.writerows(dataframe)
