#!/usr/bin/env python

import pytest

from phylo.phylo import Language


@pytest.fixture
def language():
    return Language(1000, 50)


def test_clone():
    l = language()
    m = l.clone()
    assert l._signs.forwards == m._signs.forwards
    m._signs.add(None, None)
    assert l._signs.forwards != m._signs.forwards


def test_add_link():
    l = language()
    old_signs = list(l._signs.to_pairs())
    l._add_link()
    new_signs = list(l._signs.to_pairs())
    assert len(old_signs) + 1 == len(new_signs)


def test_lose_link():
    l = language()
    old_signs = list(l._signs.to_pairs())
    l._lose_link()
    new_signs = list(l._signs.to_pairs())
    assert len(old_signs) - 1 == len(new_signs)
