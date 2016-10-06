#!/usr/bin/env python

import pytest

from phylo.phylo import Language


@pytest.fixture
def language():
    return Language(1000, 50)


def test_clone():
    l = language()
    m = l.clone()
    assert l.signs == m.signs
    m.signs.append((0, 0))
    assert l.signs != m.signs


def test_add_link():
    l = language()
    old_signs = l.signs[:]
    l._add_link()
    assert len(old_signs) + 1 == len(l.signs)


def test_lose_link():
    l = language()
    old_signs = l.signs[:]
    l._lose_link()
    assert len(old_signs) - 1 == len(l.signs)
