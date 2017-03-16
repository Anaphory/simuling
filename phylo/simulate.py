#!/usr/bin/env python

"""Main simulation runner helpers."""

import sys

import csv

from .language import Language
from .phylo import Phylogeny


def simulate(
        tree, related_concepts, initial_weight,
        concept_weight="degree_squared", scale=1, p_gain=0,
        verbose=False, tips_only=True, neighbor_factor=0.1):
    """Run a phylogeny simulation with the given parameters."""
    phy = Phylogeny(
        related_concepts,
        initial_weight=initial_weight,
        basic=[],
        tree=tree,
        scale=scale,
        neighbor_factor=neighbor_factor)

    phy.simulate(
        concept_weight=concept_weight,
        p_gain=p_gain,
        verbose=verbose)

    # "basic" is the number of words we afterwards use to to infer
    # phylogeny with neighbor-joining

    dataframe, columns = phy.collect_word_list(
        Language.vocabulary,
        collect_tips_only=tips_only)
    return columns, dataframe


def write_to_file(columns, dataframe, file=sys.stdout):
    """Write the simulation results to a file object."""
    writer = csv.writer(file, 'excel-tab')
    writer.writerow(columns)
    writer.writerows(dataframe)
