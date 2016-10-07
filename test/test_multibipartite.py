#!/usr/bin/env python

import pytest
from collections import Counter


from phylo.bipartite import MultiBipartite


@pytest.fixture
def original():
    return {1: Counter({'a': 2, 'b': 1}),
            2: Counter({'b': 1, 'c': 2})}


def test_multibipartite_inv():
    o = original()
    multibipartite = MultiBipartite(o)
    assert multibipartite.inv['a'] == Counter({1: 2})
    assert multibipartite.inv['b'] == Counter(
        {1: 1, 2: 1})
    assert multibipartite.inv['c'] == Counter({2: 2})


def test_multibipartite():
    o = original()
    multibipartite = MultiBipartite(o)
    assert multibipartite.keys() == o.keys()
    assert multibipartite.values() == set([
        x for vs in o.values() for x in vs])


def test_to_from_pairs():
    o = original()
    multibipartite = MultiBipartite(o)
    assert (MultiBipartite.from_pairs(
        multibipartite.to_pairs()).forwards == multibipartite.forwards)


def test_len():
    o = original()
    multibipartite = MultiBipartite(o)
    assert len(multibipartite) == len(list(
        multibipartite.to_pairs()))


def test_add_remove():
    o = original()
    multibipartite = MultiBipartite(o)
    l = len(multibipartite)
    multibipartite.add(None, None)
    assert len(multibipartite) == l + 1
    multibipartite.add(None, None)
    assert len(multibipartite) == l + 2
    multibipartite.remove(None, None)
    assert len(multibipartite) == l + 1
    multibipartite.remove(None, None)
    assert len(multibipartite) == l
    with pytest.raises(KeyError):
        multibipartite.remove(None, None)
