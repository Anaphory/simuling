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
    lang = Language({})
    lang._cum_concept_weights = [1, 2]
    lang._word_meaning_pairs = [(0, "a"),
                                (1, "a")]
    lang.related_concepts = {"a": ["b"], "b": ["b"]}
    return lang


@pytest.fixture
def specific_language_symmetric():
    """A language with known weights and directed transitions."""
    lang = Language({})
    lang._cum_concept_weights = [1, 2]
    lang._word_meaning_pairs = [(0, "a"),
                                (1, "a")]
    lang.related_concepts = networkx.Graph()
    lang.related_concepts.add_edges_from([("a", "b"), ("b", "b")])
    return lang


def test_clone():
    """A cloned language should be a copy-by-values.

    It should therefore start identical, but a change to the clone
    should not affect the original and vice versa.

    """
    lang = language()
    m = lang.clone()
    assert lang.flat_frequencies() == m.flat_frequencies()
    m.loss()
    assert lang.flat_frequencies() != m.flat_frequencies()


def test_add_link():
    """Adding a link should increase the number of links by one."""
    lang = language()
    old_signs = lang._word_meaning_pairs[:]
    lang.new_word()
    new_signs = lang._word_meaning_pairs[:]
    assert len(old_signs) + 1 == len(new_signs)


def test_gain():
    """The gain method should add a link."""
    lang = language()
    old_weights = lang._cum_concept_weights[-1]
    lang.gain()
    new_weights = lang._cum_concept_weights[-1]
    assert (old_weights) + 1 == (new_weights)


def test_gain_new_concept():
    """Gaining a new concept should behave in the expected manner."""
    lang = specific_language_symmetric()
    lang.gain()
    assert (
        (0, "b") in lang._word_meaning_pairs or
        (1, "b") in lang._word_meaning_pairs)


def test_loss():
    """The loss method should remove a single link."""
    lang = language()
    old_weights = sum(lang.flat_frequencies().values())
    lang.loss()
    assert (old_weights) - 1 == sum(lang.flat_frequencies().values())


def test_words_for_concept():
    """The words for a given concept should be as defined."""
    lang = specific_language()
    assert set(lang.words_for_concept("a")) == {0, 1}
