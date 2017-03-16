#!/usr/bin/env python


"""Run a language evolution model.

This module implements the CLI interface for running a very simple
forward-time phylogenetic simulation of cognate class evolution in a
language family represented by a given tree.

"""

import sys
from collections import defaultdict
import argparse
import random
import networkx
import newick

from .simulate import simulate, write_to_file


def main(args=sys.argv):
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=""" Run a very simple forward-time
    phylogenetic simulation of cognate class evolution in a language
    family.""")
    group = parser.add_argument_group("Shared properties of the languages")
    group.add_argument("--concepts", '-s', type=int, default=2000,
                       help="Number of concepts to be simulated")
    group.add_argument("--fields", '-f', type=int, default=50,
                       help="Number of semantic fields the concepts show")
    group.add_argument(
        "--semantic-network", type=argparse.FileType('r'),
        default=open("clics.gml"), # FIXME: This needs to become a path relative to __file__
        help="File containing the semantic network to be used (eg. "
        "a colexification graph) in GLM format")
    group.add_argument(
        "--min-connection",
        type=float,
        default=0,
        help="""The minimum 'weight' for a semantic network edge to be considered
        in the simulation""")
    group = parser.add_argument_group(
        "Properties of the phylogenetic simulation")
    group.add_argument(
        "trees", type=argparse.FileType("r"), nargs="+",
        help="""Files containing Newick trees (one tree per line) to be
        simulated. You can specify the same tree file multiple times
        to obtain multiple simulations.""")
    group.add_argument("--scale", type=float, default=2.39,
                       help="Scaling factor of the tree, or equivalently the "
                       "number of change events per unit of branchlength.")
    group.add_argument("--neighbor-factor", type=float, default=0.1,
                       help="How the score for implicit polysemy.")
    group.add_argument('--p-loss', type=float, default=0.0,
                       help="Probability, per time step, that a word becomes "
                       "less likely for a meaning")
    group.add_argument('--p-gain', type=float, default=0.0,
                       help="Probability, per time step, that a word gains a "
                       "related meaning")
    group.add_argument(
        '--p-new', type=float, default=0.0,
        help="Probability, per time step, that a new word arises")
    group.add_argument('--quiet', action='store_true',
                       default=False,
                       help="Do not output progress")
    group.add_argument(
        "--concept-weight",
        default="degree_squared",
        choices=["one", "degree", "degree_squared", "preferential"],
        help="Use this weight function for choosing random concepts.")
    group.add_argument(
        '--wordlist', type=str, default="{tree}-{i}.tsv",
        help="""Filename to write the word lists to.  You can use the placeholders
        {tree} to get the corresponding tree file base name (without
        file ending), and {i} for the number of the simulation (starting at `1`
        for the first simulation).""")
    group.add_argument(
        "--sample-internal-nodes", action="store_true", default=False,
        help="Sample word lists also from the tree's internal nodes")

    args = parser.parse_args(args)

    if args.semantic_network:
        related_concepts = networkx.parse_gml(args.semantic_network)
        for node1, edges in related_concepts.edge.items():
            for node2, properties in list(edges.items()):
                if properties.get("weight", 1) < args.min_connection:
                    related_concepts.remove_edge(node1, node2)
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
            dataframe, columns = simulate(
                tree, related_concepts,
                concept_weight=args.concept_weight,
                scale=args.scale,
                neighbor_factor=args.neighbor_factor,
                p_gain=args.p_gain,
                verbose=0 if args.quiet else 1,
                tips_only=not args.sample_internal_nodes)
            if args.wordlist == "-":
                wordlist_file = sys.stdout
            else:
                filename = args.wordlist.format(
                    tree=(tree_file.name).rsplit(".", 1)[0],
                    i=i)
                wordlist_file = open(filename, "w")
            write_to_file(dataframe, columns, file=wordlist_file)


if __name__ == "__main__":
    main(sys.argv[1:])
