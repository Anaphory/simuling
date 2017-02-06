#!/usr/bin/env python

"""Test some asserted properties of NamingGameLanguage."""

import pytest

from phylo.naminggame import NamingGameLanguage
from collections import defaultdict, Counter


@pytest.fixture
def naminggamelanguage():
    """Create a simple NamingGameLanguage instance."""
    n = NamingGameLanguage({1: [2], 0: [2], 2: [0, 1]})
    n.words = defaultdict(Counter,
                          {1: Counter({"one": 1, "at most one": 1}),
                           0: Counter({"zero": 1, "at most one": 1})})
    return n


def test_naminggame():
    """Test that the .change methods keeps the weight sum."""
    l = naminggamelanguage()
    cum_weight = sum(l.flat_frequencies().values())
    l.change()
    assert cum_weight == sum(l.flat_frequencies().values())


def test_clone():
    """.clone should give an independent clone with equal weights."""
    l = naminggamelanguage()
    m = l.clone()
    assert l.flat_frequencies() == m.flat_frequencies()
    m.loss()
    assert l.flat_frequencies() != m.flat_frequencies()


def test_loss():
    """Test whether .loss() reduces the sum of weights by 1."""
    l = naminggamelanguage()
    old_weights = sum(l.flat_frequencies().values())
    l.loss()
    assert (old_weights) - 1 == sum(l.flat_frequencies().values())


def test_loss_distribution():
    """Test whether .loss() is distributed proportional to weight."""
    l = NamingGameLanguage({1: []})
    samples = 10000
    words = 10
    acc = 1.1
    lost = [0] * words
    for _ in range(samples):
        # Sample many times
        l.words = defaultdict(
            Counter, {1: Counter({i: i for i in range(1, words)})})
        l.loss()

        # Find which word was lost
        for i in range(1, words):
            if l.words[1][i] < i:
                lost[i] += 1
                break
        else:
            raise AssertionError("No word reduced weight")

    # Check that loss is distributed proportional to weight
    print(lost)
    lost = [lost[i] / i
            for i in range(1, words)]
    lost1 = sum(lost) / (words - 1)
    for i in range(1, words - 1):
        assert lost1 * acc >= lost[i] >= lost1 / acc
