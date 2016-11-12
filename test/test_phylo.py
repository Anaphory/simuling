#!/usr/bin/env python

import pytest

from phylo.phylo import Language


@pytest.fixture
def language():
    return Language({"a": ["b", "c"],
                     "b": ["a"],
                     "c": ["b"]})


def specific_language():
    l = Language({})
    l._cum_concept_weights = [1, 2]
    l._word_meaning_pairs = [(0, "a"),
                             (1, "a")]
    return l


def test_clone():
    l = language()
    m = l.clone()
    assert l._word_meaning_pairs == m._word_meaning_pairs
    m.new_word()
    assert l._word_meaning_pairs != m._word_meaning_pairs


def test_add_link():
    l = language()
    old_signs = l._word_meaning_pairs[:]
    l.new_word()
    new_signs = l._word_meaning_pairs[:]
    assert len(old_signs) + 1 == len(new_signs)


def test_gain():
    l = language()
    old_weights = l._cum_concept_weights[-1]
    l.gain()
    new_weights = l._cum_concept_weights[-1]
    assert (old_weights) + 1 == (new_weights)


def test_loss():
    l = language()
    old_weights = l._cum_concept_weights[-1]
    l.loss()
    new_weights = l._cum_concept_weights[-1]
    assert (old_weights) - 1 == (new_weights)


def test_words_for_concept():
    l = specific_language()
    assert set(l.words_for_concept("a")) == {0, 1}
