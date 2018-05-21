#!/usr/bin/env python

"""Generate the data to assess simulation robustness.

Run the simulation on a long branch with parameter variation.
"""

import csv
import numpy
import itertools
import numpy.random as random

import argparse

import newick

from .phylo.naminggame import concept_weights
from .phylo.simulate import simulate, factory
from .defaults import defaults

id = random.randint(0x10000)

initial_weights = {
    "1": lambda: 1,
    "6": lambda: 6,
    "10": lambda: 10,
    "20": lambda: 20,
    "30": lambda: 30,
    "60": lambda: 60,
    "100": lambda: 100,
    "200": lambda: 200,
    "400": lambda: 400,
    "800": lambda: 800,
    # "d10": lambda: random.randint(1, 11),
    # "d60": lambda: random.randint(1, 61),
    # "d199": lambda: random.randint(1, 200),
    # "geom5": lambda: random.geometric(1/5.5),
    # "geom100": lambda: random.geometric(1/100),
    # "poisson5": lambda: random.poisson(5.5),
    # "poisson100": lambda: random.poisson(100),
    # "pareto": lambda: int(random.pareto(0.4)),
    # "fpareto5": lambda: int(random.pareto(2) * 5.6 + 0.5),
    # "fpareto100": lambda: int(random.pareto(2) * 100 + 0.5)
}

parser = argparse.ArgumentParser(
    description="Run long simulations on branch lengths")
parser.add_argument("--stop", action="store_true", default=False,
                    help="Stop simulating after the supplied steps")
parser.add_argument("loglength", nargs=argparse.REMAINDER, type=int,
                    help="Branch lengths to simulate: i → 2^(20+i)")
args = parser.parse_args()
start = max(args.loglength, default=0) + 1

for run in itertools.chain(args.loglength,
                           [] if args.stop else itertools.count(start=start)):
    long_tree = newick.Node("1", "1")
    tip = long_tree
    for i in range(20 + run):
        old_tip = tip
        tip = newick.Node(
            str(2 ** (i + 1)),
            str(2**i))
        old_tip.add_descendant(tip)

    print(long_tree.newick)

    print("Generic")
    try:
        with open(
                "trivial_long_branch{:x}_r{:d}_i100_w2_n0.004.csv".format(
                    id + 1, run), 'w') as file:
            writer = csv.writer(file)
            writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                             "Weight", "Cognate_Set", "Concept_CogID"))
            for dataframe in simulate(
                    long_tree,
                    tips_only=False,
                    **defaults):
                writer.writerows(dataframe)
    except KeyboardInterrupt:
        pass

    for name, distribution in initial_weights.items():
        print("X_I:", name)
        parameters = defaults.copy()
        parameters["initial_weight"] = distribution
        try:
            with open(
                    "trivial_long_branch{:x}_r{:d}_i{:}_w2_n0.004.csv".format(
                        id, run, name), 'w') as file:
                writer = csv.writer(file)
                writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                                 "Weight", "Cognate_Set", "Concept_CogID"))
                for dataframe in simulate(
                        long_tree,
                        tips_only=False,
                        **parameters):
                    writer.writerows(dataframe)
        except KeyboardInterrupt:
            pass

    for neighbor_factor in numpy.array([
            0., 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1., 1.2])/25:
        print("n:", neighbor_factor)
        parameters = defaults.copy()
        parameters["related_concepts_edge_weight"] = factory(neighbor_factor)
        try:
            with open(
                    "trivial_long_branch{:x}_r{:d}_id199_w2_n{:f}.csv".format(
                        id, run, neighbor_factor), 'w') as file:
                writer = csv.writer(file)
                writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                                 "Weight", "Cognate_Set", "Concept_CogID"))
                for dataframe in simulate(
                        long_tree,
                        tips_only=False,
                        **parameters):
                    writer.writerows(dataframe)
        except KeyboardInterrupt:
            pass

    for name, c_weight in concept_weights.items():
        print(name)
        parameters = defaults.copy()
        parameters["concept_weight"] = c_weight
        try:
            with open(
                    "trivial_long_branch{:x}_r{:d}_id199_c{:s}_w2_n0.004.csv"
                    "".format(id, run, name), 'w') as file:
                writer = csv.writer(file)
                writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                                 "Weight", "Cognate_Set", "Concept_CogID"))
                for dataframe in simulate(
                        long_tree,
                        tips_only=False,
                        **parameters):
                    writer.writerows(dataframe)
        except KeyboardInterrupt:
            pass

    for losswt in [
            lambda x: x,
            lambda x: 1,
            lambda x: 1 / x]:
        print("losswt(2):", losswt(2))
        parameters = defaults.copy()
        parameters["losswt"] = losswt
        try:
            with open(
                    "trivial_long_branch{:x}_r{:d}_id199_w{:f}_n0.004.csv"
                    "".format(
                        id, run, losswt(2)), 'w') as file:
                writer = csv.writer(file)
                writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                                 "Weight", "Cognate_Set", "Concept_CogID"))
                for dataframe in simulate(
                        long_tree,
                        tips_only=False,
                        **parameters):
                    writer.writerows(dataframe)
        except KeyboardInterrupt:
            pass
