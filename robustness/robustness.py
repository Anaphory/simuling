#!/usr/bin/env python

"""Generate the data to assess simulation robustness.

Run the simulation on a long branch with parameter variation.
"""

import os
import numpy.random as random

import newick
import networkx

from phylo.simulate import simulate, write_to_file

long_tree = newick.Node("1", "1")
tip = long_tree
for i in range(22):
    old_tip = tip
    tip = newick.Node(
        str(2 ** (i+1)),
        str(2**i))
    old_tip.add_descendant(tip)

print(long_tree.newick)

clics = open(os.path.join(
    os.path.dirname(__file__), "..", "phylo", "clics.gml"))
clics_concepts = networkx.parse_gml(clics)

initial_weights = {
    "1": lambda: 1,
    "6": lambda: 6,
    "10": lambda: 10,
    "100": lambda: 100,
    "d10": lambda: random.randint(1, 11),
    "geom": lambda: random.geometric(1/5.5),
    "poisson": lambda: random.poisson(5.5),
    "pareto": lambda: int(random.pareto(0.4)),
    "fpareto": lambda: int(random.pareto(5.5))
    }

for name, distribution in initial_weights.items():
    dataframe, columns = simulate(
        long_tree,
        clics_concepts,
        initial_weight=distribution,
        concept_weight='degree_squared',
        scale=1,
        neighbor_factor=0.1,
        p_gain=0,
        verbose=0,
        tips_only=False)
    write_to_file(dataframe, columns,
                  file=open("trivial_long_branch_i{:}.tsv".format(
                      name), 'w'))

for run in range(16):
    dataframe, columns = simulate(
        long_tree,
        clics_concepts,
        initial_weight=lambda: random.randint(1, 11),
        concept_weight='degree_squared',
        scale=1,
        neighbor_factor=0.1,
        p_gain=0,
        verbose=0,
        tips_only=False)
    write_to_file(dataframe, columns,
                  file=open("trivial_long_branch_{:d}.tsv".format(run), 'w'))

for neighbor_factor in [
        0., 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1., 1.2]:
    dataframe, columns = simulate(
        long_tree,
        clics_concepts,
        initial_weight=lambda: random.randint(1, 11),
        concept_weight='degree_squared',
        scale=1,
        neighbor_factor=neighbor_factor,
        p_gain=0,
        verbose=0,
        tips_only=False)
    write_to_file(dataframe, columns,
                  file=open("trivial_long_branch_n{:f}.tsv".format(
                      neighbor_factor),
                            'w'))
