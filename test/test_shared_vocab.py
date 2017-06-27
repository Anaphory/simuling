#!/usr/bin/env python

"""Test shared vocabulary calculations."""

import pytest

import pandas

import simuling.calibration.compare_simulation_with_data as compare


@pytest.fixture
def wordlist():
    """Example word list."""
    length = 12
    return pandas.DataFrame(
        {"Language_ID": [0]*length,
         "Feature_ID": range(length),
         "Value": range(length)})


def test_pairwise_shared_vocabulary_equal():
    """Check that two equal languages return pairwise_shared_vocabulary 1."""
    v1 = wordlist()
    v2 = v1.copy()
    v2["Language_ID"] = -1
    vocabulary = v1.append(v2)
    for (language1, language2), score in compare.pairwise_shared_vocabulary(
            vocabulary):
        assert score == 1


def test_pairwise_shared_vocabulary_half():
    """Check that two half-similar languages return psv 0.5 when compared."""
    v1 = wordlist()
    v2 = v1.copy()
    if len(v2) % 2 == 1:
        return
    v2["Language_ID"] = -1
    for i, row in v2.iterrows():
        v2.set_value(i, "Value", -1)
    vocabulary = v1.append(v2)
    for (language1, language2), score in compare.pairwise_shared_vocabulary(
            vocabulary):
        assert score == 0.5


def test_pairwise_shared_vocabulary_synonyms():
    """Check that ambiguous vocabulary matches work as expected."""
    v1 = wordlist()

    v2 = v1.copy()
    v2["Language_ID"] = -1
    v2synonyms = v2.copy()
    v2synonyms["Value"] = -1

    vocabulary = v1.append(v2).append(v2synonyms)

    for (language1, language2), score in compare.pairwise_shared_vocabulary(
            vocabulary):
        assert score == 0.5


def test_pairwise_shared_vocabulary_ident_synonyms():
    """Check that ambiguous vocabulary matches work as expected."""
    v1 = wordlist()
    v1synonyms = v1.copy()
    v1synonyms["Value"] = -1
    v1 = v1.append(v1synonyms)

    v2 = v1.copy()
    v2["Language_ID"] = -1

    vocabulary = v1.append(v2)

    for (language1, language2), score in compare.pairwise_shared_vocabulary(
            vocabulary):
        assert score == 1.0
