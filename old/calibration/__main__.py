#!/usr/bin/env python

"""Iteratively optimize the simulation scale.

Run simulations at various scales of trees and compare them with
real-world data to find the best scale between tree and simulation
steps.

"""

import os
import sys
import argparse
import tempfile

import newick
import networkx

from ..defaults import defaults
from ..phylo.simulate import factory
from .compare_simulation_with_data import (
    read_cldf)

from ..phylo.naminggame import NamingGameLanguage as Language

from .util import run_sims_and_calc_lk, cached_realdata


def argparser(args=sys.argv):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--realdata",
        default=open(os.path.join(os.path.dirname(__file__),
                                  "beijingdaxue1964.csv")),
        type=argparse.FileType("r"),
        help="Word list from real life")
    parser.add_argument(
        "--tree",
        default=open(os.path.join(os.path.dirname(__file__),
                                  "dated.tre")),
        type=argparse.FileType("r"),
        help="The reconstructed, dated tree (Newick) that underlies the data")
    parser.add_argument(
        "--minscale",
        type=float,
        default=10,
        help="The minimum scale to use")
    parser.add_argument(
        "--maxscale",
        type=float,
        default=200,
        help="The maximum scale to use")
    parser.add_argument(
        "--sims",
        type=int,
        default=3,
        help="How many simulations to run for each scale")
    parser.add_argument(
        "--dir", "--directory",
        default=tempfile.mkdtemp(prefix="calibrate"),
        help="Write simulation results to this directory")

    parser.add_argument(
        "--init-wordlist",
        help="""A file containing a word list which will be used as starting
        point, instead of running 10^7 simulation steps ahead""")
    parser.add_argument(
        "--init-language",
        help="""The language ID to be taken from
            INIT_WORDLIST as starting point (default:
        The language from the last row in the file)""")

    parser.add_argument(
        "--semantic-network",
        default=open(os.path.join(os.path.dirname(__file__),
                                  "../phylo/network-3-families.gml")),
        type=argparse.FileType("r"),
        help="""File containing the semantic network to be used (eg. a
        colexification graph) in GLM format""")
    parser.add_argument(
        "--weight-name",
        default="FamilyWeight",
        help="Name of the weight attribute in the GML file")
    parser.add_argument(
        "--initial-weight",
        default=None,
        type=int,
        help="""Initial weight value for all words""")
    parser.add_argument(
        "--neighbor-factor",
        type=float,
        default=None,
        help="Score for implicit polysemy along branches.")
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="""Ignore these pairs of languages.
        Pairs are separated by colons (":").
        For example --ignore Chaozou:Xiamen""")
    parser.add_argument(
        "--sample-threshold", "--threshold",
        default=180,
        help="Weight threshold to sample a word")
    args = parser.parse_args(args)
    return args


def main(args):
    """Run the CLI."""
    args = argparser(args)

    parameters = defaults.copy()
    if args.neighbor_factor is not None:
        parameters["related_concepts_edge_weight"] = factory(
            args.neighbor_factor)
    if args.initial_weight is not None:
        parameters["initial_weight"] = lambda x: args.initial_weight

    related_concepts = networkx.parse_gml(args.semantic_network)

    lks = {}
    lower = args.minscale
    upper = args.maxscale

    tree = newick.load(args.tree)[0]
    if args.init_wordlist is None:
        virtual_root = newick.Node()
        virtual_root.add_descendant(tree)
        tree.length = 10000000
        tree = virtual_root
        starting_data = None
    else:
        raw_data = read_cldf(args.init_wordlist, top_word_only=False)
        init_language = args.init_language or str(
            list(raw_data["Language_ID"])[-1])
        raw_data = raw_data[
            raw_data["Language_ID"].astype(str) == init_language]
        starting_data = Language(
            related_concepts,
            related_concepts_edge_weight=parameters[
                "related_concepts_edge_weight"],
            generate_words=False)
        maxword = 0
        for r, row in raw_data.iterrows():
            meaning = row["Feature_ID"]
            weight = row["Weight"]
            i = row["Cognate_Set"]
            maxword = max(i, maxword)
            starting_data.words[meaning]["{:}-{:}".format(meaning, i)] = weight
        Language.max_word = maxword

    os.chdir(args.dir)

    ignore = []
    if args.ignore:
        for i in args.ignore:
            ignore.append(i.split(":"))

    realdata = cached_realdata(args.realdata)

    def simulate_scale(scale):
        parameters["scale"] = scale
        return run_sims_and_calc_lk(
            n_sim=args.sims,
            tree=tree,
            realdata=realdata,
            sample_threshold=args.sample_threshold,
            ignore=ignore,
            root=starting_data,
            **parameters)

    lks[lower] = simulate_scale(lower)
    lks[upper] = simulate_scale(upper)
    while upper / lower > 1.001:
        i = (lower**2 * upper) ** (1 / 3)
        lks[i] = simulate_scale(i)
        with open("lks", "a") as w:
            print("{:13.2f} {:13.2f}".format(i, lks[i]))
        if lks[i] < lks[lower] and lks[i] < lks[upper]:
            break

        j = (lower * upper**2) ** (1 / 3)
        lks[j] = simulate_scale(j)
        with open("lks", "a") as w:
            print("{:13.2f} {:13.2f}".format(j, lks[j]), file=w)
        if lks[j] < lks[lower] and lks[j] < lks[upper]:
            break

        max_lk_at = max(lks, key=lks.get)
        try:
            upper = min(i for i in lks if i > max_lk_at)
        except ValueError:
            pass
        try:
            lower = max(i for i in lks if i < max_lk_at)
        except ValueError:
            pass

    print("Simulation likelihoods:")
    for x in sorted(lks):
        print("{:13f} {:13f}".format(x, lks[x]))


if __name__ == '__main__':
    main(sys.argv[1:])
