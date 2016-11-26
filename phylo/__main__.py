#!/usr/bin/env python

from collections import defaultdict
import argparse
import random
import networkx


from .cli import (run, basic_vocabulary_sampler)
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
                   help="Files containing Newick trees to be simulated. You can specify the same tree file multiple times to obtain multiple simulations.")
group.add_argument('--p-lose', type=float, default=0.5,
                   help="Probability, per time step, that a word becomes "
                   "less likely for a meaning")
group.add_argument('--p-gain', type=float, default=0.4,
                   help="Probability, per time step, that a word gains a "
                   "related meaning")
group.add_argument('--p-new', type=float, default=0.1,
                   help="Probability, per time step, that a new word arises")
group.add_argument(
    '--wordlist', type=str, default="simulation",
    help="Filename to write the word lists to. '"
    "-{run_number:}.tsv' is appended automatically.")


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

run(related_concepts=related_concepts,
    wordlist_filename=args.wordlist,
    tree_filename=args.trees,
    samplers=[("", Language.vocabulary)])
