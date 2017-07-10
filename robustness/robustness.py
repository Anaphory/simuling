#!/usr/bin/env python

"""Generate the data to assess simulation robustness.

Run the simulation on a long branch with parameter variation.
"""

import os
import numpy.random as random

import newick
import networkx

import simuling.phylo as phylo
from simuling.phylo.simulate import simulate, write_to_file


def factory(n):
    """An edge weight extractor factory.

    Return a function that returns the 'weight' attribute of its first
    argument, scaled by n.

    """
    def scaled_weight_threshold(x):
        if x['FamilyWeight'] < 2:
            return 0
        else:
            return n * x['FamilyWeight']
    return scaled_weight_threshold


clics = open(os.path.join(
    os.path.dirname(phylo.__file__), "network-3-families.gml"))
clics_concepts = networkx.parse_gml(clics)

initial_weights = {
    "1": lambda: 1,
    "6": lambda: 6,
    "10": lambda: 10,
    "20": lambda: 20,
    "30": lambda: 30,
    "60": lambda: 60,
    "100": lambda: 100,
    "d10": lambda: random.randint(1, 11),
    "d60": lambda: random.randint(1, 61),
    "geom": lambda: random.geometric(1/5.5),
    "poisson": lambda: random.poisson(5.5),
    "pareto": lambda: int(random.pareto(0.4)),
    "fpareto": lambda: int(random.pareto(2) * 5.6 + 0.5)
    }

for run in range(16):
    long_tree = newick.Node("1", "1")
    tip = long_tree
    for i in range(20 + run):
        old_tip = tip
        tip = newick.Node(
            str(2 ** (i+1)),
            str(2**i))
        old_tip.add_descendant(tip)

    print(long_tree.newick)

    dataframe, columns = simulate(
        long_tree,
        clics_concepts,
        initial_weight=lambda: random.randint(1, 11),
        concept_weight='degree_squared',
        scale=1,
        related_concepts_edge_weight=factory(0.004),
        p_gain=0,
        verbose=0,
        tips_only=False)
    write_to_file(dataframe, columns,
                  file=open("trivial_long_branch_{:d}.tsv".format(run), 'w'))

    for name, distribution in initial_weights.items():
        print(name)
        dataframe, columns = simulate(
            long_tree,
            clics_concepts,
            initial_weight=distribution,
            concept_weight='degree_squared',
            scale=1,
            related_concepts_edge_weight=factory(0.004),
            p_gain=0,
            verbose=0,
            tips_only=False)
        write_to_file(dataframe, columns,
                      file=open(
                          "trivial_long_branch_{:d}_i{:}.tsv".format(
                              run, name), 'w'))

    for neighbor_factor in [
            0., 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1., 1.2]:
        print(neighbor_factor/25)
        dataframe, columns = simulate(
            long_tree,
            clics_concepts,
            initial_weight=lambda: random.randint(1, 11),
            concept_weight='degree_squared',
            scale=1,
            related_concepts_edge_weight=factory(neighbor_factor/25),
            p_gain=0,
            verbose=0,
            tips_only=False)
        write_to_file(dataframe, columns,
                      file=open("trivial_long_branch_{:d}_n{:f}.tsv".format(
                          run, neighbor_factor/25),
                                'w'))
