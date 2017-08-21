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

import simuling.phylo as phylo
from pyconcepticon.api import Concepticon
from simuling.phylo.simulate import simulate, write_to_file
from .compare_simulation_with_data import (
    read_cldf, estimate_normal_distribution, normal_likelihood,
    pairwise_shared_vocabulary)


def simulate_and_write(tree, features, related_concepts, scale=1,
                       n_sim=3, initial_weight=6,
                       related_concepts_edge_weight=lambda x: x):
    """Simulate evolution on tree and write results to file."""
    for i in range(n_sim):
        columns, dataframe = simulate(
            tree, related_concepts, initial_weight=lambda: initial_weight,
            related_concepts_edge_weight=related_concepts_edge_weight,
            scale=scale, verbose=True)
        filename = "simulation_{:}_{:}.tsv".format(scale, i)
        with open(filename, "w") as f:
            write_to_file(columns, dataframe, f)
        yield read_cldf(filename, features=features)


def run_sims_and_calc_lk(tree, realdata, features, related_concepts,
                         scale=1, n_sim=3, initial_weight=6,
                         related_concepts_edge_weight=lambda x: x,
                         ignore=[], normal=False):
    """Run simulations and calculate their Normal likelihood.

    Run `n` simulations and calculate the likelihood of `realdata`
    under a Normal distribution assumption of pairwise shared vocabulary
    proportions give the results of the simulations.

    """
    if normal:
        normals = estimate_normal_distribution(simulate_and_write(
            tree, features=features, related_concepts=related_concepts,
            related_concepts_edge_weight=related_concepts_edge_weight,
            scale=scale, n_sim=n_sim))
        return normal_likelihood(realdata, normals,
                                 ignore=ignore)
    else:
        neg_squared_error = 0
        for simulation in simulate_and_write(
                tree, features=features, related_concepts=related_concepts,
                related_concepts_edge_weight=related_concepts_edge_weight,
                scale=scale, n_sim=n_sim):
            for (l1, l2), score in (
                    pairwise_shared_vocabulary(simulation, False)):
                if l1 > l2:
                    l1, l2 = l2, l1
                if (l1, l2) in ignore:
                    continue
                error = (realdata[l1, l2] - score) ** 2
                print(l1, l2, score, error)
                neg_squared_error -= error
        return neg_squared_error/n_sim


def main(args):
    """Run the CLI."""
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
        default=0.2,
        help="The minimum scale to use")
    parser.add_argument(
        "--maxscale",
        type=float,
        default=15,
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
        "--features",
        default="Swadesh-1964-215",
        help="""The list of concepts to down-sample to. Either the ID of a list in
        concepticon, or a comma-separated list of glosses.""")

    parser.add_argument(
        "--semantic-network",
        # FIXME: This needs to become a path relative to __file__
        default=open(os.path.join(os.path.dirname(phylo.__file__),
                                  "network-3-families.gml")),
        type=argparse.FileType("r"),
        help="""File containing the semantic network to be used (eg. a
        colexification graph) in GLM format""")
    parser.add_argument(
        "--weight-name",
        default="FamilyWeight",
        help="Name of the weight attribute in the GML file")
    parser.add_argument(
        "--initial-weight",
        default=6,
        type=int,
        help="""Initial weight value for all words""")
    parser.add_argument(
        "--neighbor-factor",
        type=float,
        default=0.004,
        help="Score for implicit polysemy along branches.")
    parser.add_argument(
        "--min-connection",
        type=float,
        default=0,
        help="""The minimum 'weight' for a semantic network edge to be considered
        in the simulation""")
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="""Ignore these pairs of languages.
        Pairs are separated by colons (":").
        For example --ignore Chaozou:Xiamen""")

    args = parser.parse_args(args)

    related_concepts = networkx.parse_gml(args.semantic_network)
    for node1, edges in related_concepts.edge.items():
        for node2, properties in list(edges.items()):
            if properties.get("weight", 1) < args.min_connection:
                related_concepts.remove_edge(node1, node2)

    os.chdir(args.dir)
    lks = {}
    lower = args.minscale
    upper = args.maxscale

    tree = newick.load(args.tree)[0]
    data = read_cldf(args.realdata)

    if args.features != '*':
        try:
            import pdb
            pdb.set_trace()
            features = [
                int(c.concepticon_id)
                for c in Concepticon().conceptlists[
                    args.features].concepts.values()]
        except KeyError:
            features = args.features.split(",")
    else:
        features = None

    ignore = []
    if args.ignore:
        for i in args.ignore:
            ignore.append(i.split(":"))

    realdata = {pair: score
                for pair, score in pairwise_shared_vocabulary(data)}

    def scaled_weight_threshold(x):
        if x[args.weight_name] < args.min_connection:
            return 0
        else:
            return args.neighbor_factor * x[args.weight_name]

    def simulate_scale(scale):
        return run_sims_and_calc_lk(
            scale=scale,
            n_sim=args.sims,
            related_concepts=related_concepts,
            tree=tree,
            initial_weight=args.initial_weight,
            related_concepts_edge_weight=scaled_weight_threshold,
            realdata=realdata,
            features=features,
            ignore=ignore)

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