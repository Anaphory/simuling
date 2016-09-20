from simuling import *
import pytest

import networkx


@pytest.fixture(params=[networkx.krackhardt_kite_graph(),
                        networkx.binomial_graph(8, 0.5, seed=0)])
def lfs(request):
    return LanguageForwardSimulation(request.param, 0)


@pytest.fixture
def speaker():
    return Speaker()


def test_speaker_is_set(lfs):
    assert lfs.population_graph.node[0]['speaker'], (
        "Node 0 should have a speaker attached")


def test_run_lfs(lfs):
    lfs.run(100)


def test_time_step(lfs):
    before = networkx.Graph(lfs.population_graph)
    lfs.run(1)
    after = lfs.population_graph
    diff = 0
    for node in before.nodes():
        assert node in after.nodes()
        if before.node[node]['speaker'] != after.node[node]['speaker']:
            print(before.node[node]['speaker'], after.node[node]['speaker'])
            diff += 1
    assert diff == 1


def test_random_speaker(lfs):
    nodes = lfs.population_graph.nodes()
    # FIXME: There are cleaner ways to run stochastic tests, use one.
    counter = {node: 0 for node in nodes}
    k = 10000
    for _ in range(len(nodes)*k):
        counter[lfs.random_speaker()] += 1
    for val in counter.values():
        assert k*0.9 < val < k/0.9


def test_random_speaker_among(lfs):
    speakers = {0: {}, 1: {}}
    # FIXME: There are cleaner ways to run stochastic tests, use one.
    counter = {id(lfs.population_graph.node[i]['speaker']): 0
               for i in speakers}
    k = 10000
    for _ in range(len(speakers)*k):
        counter[id(lfs.random_speaker_among(speakers))] += 1
    for val in counter.values():
        assert k*0.9 < val < k/0.9
