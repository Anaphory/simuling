#!/usr/bin/env python

import pytest

from phylo.bipartite import Bipartite


@pytest.fixture
def original():
    return {1: set(['a', 'b']),
            2: set(['b', 'c'])}


def test_bipartit_inv():
    o = original()
    bipartite = Bipartite(o)
    assert bipartite.inv['a'] == {1}
    assert bipartite.inv['b'] == {1, 2}
    assert bipartite.inv['c'] == {2}


def test_bipartite():
    o = original()
    bipartite = Bipartite(o)
    assert bipartite.keys() == o.keys()
    assert bipartite.values() == set([
        x for vs in o.values() for x in vs])


def test_to_from_pairs():
    o = original()
    bipartite = Bipartite(o)
    assert (Bipartite.from_pairs(
        bipartite.to_pairs()).forwards == bipartite.forwards)
