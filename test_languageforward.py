from languageforward import *
import pytest

import networkx


@pytest.fixture(params=[networkx.krackhardt_kite_graph(),
                        networkx.binomial_graph(8, 0.5, seed=0)])
def lfs(request):
    return LanguageForwardSimulation(request.param, 0)


def test_speaker_is_set(lfs):
    assert lfs.population_graph.node[0]['speaker'], (
        "Node 0 should have a speaker attached")


def test_run_lfs(lfs):
    lfs.run(100)


def test_time_step(lfs):
    lfs.run(1)
