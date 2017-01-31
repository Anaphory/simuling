#!/usr/bin/env python

import pytest

from phylo.naminggame import NamingGameLanguage
from collections import defaultdict, Counter


@pytest.fixture
def naminggamelanguage():
    n = NamingGameLanguage({1: [2], 0: [2], 2: [0, 1]})
    n.words = defaultdict(Counter,
                          {1: Counter({"one": 1, "at most one": 1}),
                           0: Counter({"zero": 1, "at most one": 1})})
    return n


def test_naminggame():
    l = naminggamelanguage()
    cum_weight = sum(l.flat_frequencies().values())
    l.change()
    assert cum_weight == sum(l.flat_frequencies().values())


def test_clone():
    l = naminggamelanguage()
    m = l.clone()
    assert l.flat_frequencies() == m.flat_frequencies()
    m.loss()
    assert l.flat_frequencies() != m.flat_frequencies()


def test_loss():
    l = naminggamelanguage()
    old_weights = sum(l.flat_frequencies().values())
    l.loss()
    assert (old_weights) - 1 == sum(l.flat_frequencies().values())
