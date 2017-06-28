#!/usr/bin/env python

"""Test core language evolution functionality."""

import networkx

import pytest

from simuling.phylo.language import Language


@pytest.fixture
def language():
    """A random language."""
    return Language({"a": ["b", "c"],
                     "b": ["a"],
                     "c": ["b"]})


@pytest.fixture
def specific_language():
    """A language with known weights and transitions."""
    l = Language({})
    l._cum_concept_weights = [1, 2]
    l._word_meaning_pairs = [(0, "a"),
                             (1, "a")]
    l.related_concepts = {"a": ["b"], "b": ["b"]}
    return l


@pytest.fixture
def specific_language_symmetric():
    """A language with known weights and directed transitions."""
    l = Language({})
    l._cum_concept_weights = [1, 2]
    l._word_meaning_pairs = [(0, "a"),
                             (1, "a")]
    l.related_concepts = networkx.Graph()
    l.related_concepts.add_edges_from([("a", "b"), ("b", "b")])
    return l


def test_clone():
    """A cloned language should be a copy-by-values.

    It should therefore start identical, but a change to the clone
    should not affect the original and vice versa.

    """
    l = language()
    m = l.clone()
    assert l.flat_frequencies() == m.flat_frequencies()
    m.loss()
    assert l.flat_frequencies() != m.flat_frequencies()


def test_add_link():
    """Adding a link should increase the number of links by one."""
    l = language()
    old_signs = l._word_meaning_pairs[:]
    l.new_word()
    new_signs = l._word_meaning_pairs[:]
    assert len(old_signs) + 1 == len(new_signs)


def test_gain():
    """The gain method should add a link."""
    l = language()
    old_weights = l._cum_concept_weights[-1]
    l.gain()
    new_weights = l._cum_concept_weights[-1]
    assert (old_weights) + 1 == (new_weights)


def test_gain_new_concept():
    """Gaining a new concept should behave in the expected manner."""
    l = specific_language_symmetric()
    l.gain()
    assert (
        (0, "b") in l._word_meaning_pairs or
        (1, "b") in l._word_meaning_pairs)


def test_loss():
    """The loss method should remove a single link."""
    l = language()
    old_weights = sum(l.flat_frequencies().values())
    l.loss()
    assert (old_weights) - 1 == sum(l.flat_frequencies().values())


def test_words_for_concept():
    """The words for a given concept should be as defined."""
    l = specific_language()
    assert set(l.words_for_concept("a")) == {0, 1}
