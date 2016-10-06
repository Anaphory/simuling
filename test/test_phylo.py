#!/usr/bin/env python

import pytest

from phylo.phylo import Language


@pytest.fixture
def language():
    return Language(1000, 50)


def test_clone():
    l = language()
    m = l.clone()
    assert set(l.signs) == set(m.signs)
    m._signs.add(None, None)
    assert set(l.signs) != set(m.signs)


def test_add_link():
    l = language()
    old_signs = list(l.signs)
    l._add_link()
    new_signs = list(l.signs)
    assert len(old_signs) + 1 == len(new_signs)


def test_lose_link():
    l = language()
    old_signs = list(l.signs)
    l._lose_link()
    new_signs = list(l.signs)
    assert len(old_signs) - 1 == len(new_signs)
