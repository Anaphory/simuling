#!/usr/bin/env python

import pytest

from phylo.naminggame import NamingGameLanguage
from collections import defaultdict, Counter


@pytest.fixture
def naminggamelanguage():
    n = NamingGameLanguage({1: [], 0: []})
    n.words = defaultdict(Counter,
                          {1: Counter({"one": 1, "at most one": 1}),
                           0: Counter({"zero": 1, "at most one": 1})})
    return n


def test_naminggame():
    l = naminggamelanguage()
    cum_weight = sum(w
                     for words in l.words.values()
                     for w in words.values())
    l.change()
    assert cum_weight == sum(w
                             for words in l.words.values()
                             for w in words.values())
