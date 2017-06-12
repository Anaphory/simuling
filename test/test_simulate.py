#!/usr/bin/env python

"""Test the `simulate` module.

That module provides wrapper functions for running the whole
simulation.

"""

import newick

import phylo.simulate as simulate


def test_simulate():
    """Check that a basic simulation runs."""
    simulate.simulate(
        tree=newick.loads("(A:1):1")[0],
        related_concepts={"a": ["b"], "b": ["a"]},
        initial_weight=lambda: 10,
        concept_weight='one',
        scale=2,
        neighbor_factor=0.1,
        p_gain=0.1,
        verbose=0,
        tips_only=True)
