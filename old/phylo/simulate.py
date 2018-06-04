#!/usr/bin/env python

"""Main simulation runner helpers."""

import sys

import csv

from .naminggame import NamingGameLanguage as Language
from .phylo import Phylogeny


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


def simulate(
        tree, related_concepts, initial_weight,
        concept_weight="degreesquared", scale=1, p_gain=0,
        verbose=False, tips_only=True,
        losswt=lambda x: x,
        related_concepts_edge_weight=lambda x: 0.1 * x,
        root=None):
    """Run a phylogeny simulation with the given parameters."""
    if root is None:
        root = Language(
            related_concepts,
            related_concepts_edge_weight=related_concepts_edge_weight,
            generate_words=False)
        root.generate_words(initial_weight)

    phy = Phylogeny(
        basic=[],
        tree=tree,
        root=root,
        losswt=losswt,
        scale=scale)

    for language in phy.simulate(
            concept_weight=concept_weight,
            p_gain=p_gain,
            verbose=verbose):

        dataframe = phy.collect_word_list(
            Language.vocabulary,
            collect_language=language,
            collect_tips_only=tips_only)
        yield dataframe


def write_to_file(columns, dataframe, file=sys.stdout):
    """Write the simulation results to a file object."""
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(dataframe)
