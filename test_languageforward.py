from languageforward import *
import pytest

import networkx


@pytest.fixture
def lfs():
    return LanguageForwardSimulation(networkx.krackhardt_kite_graph(), 0)


def test_speaker_is_set(lfs):
    assert lfs.population_graph.node[0]['speaker'], (
        "Node 0 should have a speaker attached")
