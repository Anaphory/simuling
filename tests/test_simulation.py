import collections
from pathlib import Path

import newick

from simuling.simulation import SemanticNetwork, Language


# Tests
def test_dumb_semantic_loader():
    """Is the default semantic network available?"""
    from simuling.cli import default_network
    SemanticNetwork.load_from_gml(
        default_network.open(),
        "FamilyWeight")


def test_semantic_weight():
    """Does a semantic network have expected edge weights?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    assert s.edge_weight("left", "right") == 2 * 0.004


def test_semantic_concept_weight():
    """Does a semantic network have the expected concept weights?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    assert s.concept_weight("left") == 1 ** 2


def test_semantic_random():
    """Does the network produce the expected distribution of meanings?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    c = collections.Counter()
    for i in range(200):
        c[s.random()] += 1
    assert c["off"] == 0
    assert 80 < c["left"] < 120
    assert c["left"] + c["right"] == 200


def test_language_wn():
    """Does the language have the expected weights for related concepts?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    lg = Language({"top": collections.defaultdict(lambda: 0, {0: 10})},
                  s)
    assert lg.weighted_neighbors("left") == {'right': 0.008, 'left': 1}


def test_language_cs():
    """Does the language calculate the scores correctly?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    lg = Language({"left": collections.defaultdict(lambda: 0, {0: 10})},
                  s)
    assert lg.calculate_scores("left") == {0: 10}
    assert lg.calculate_scores("right") == {0: 0.08}


def test_language_re():
    """Does the language provide the right weighted distribution of edges?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    lg = Language({"top": collections.defaultdict(lambda: 0, {0: 10}),
                   "left": collections.defaultdict(lambda: 0, {0: 10})},
                  s)
    c = collections.Counter()
    for i in range(200):
        c[lg.random_edge()] += 1
    assert c[("right", 0)] == 0
    assert 80 < c[("left", 0)] < 120
    assert c[("left", 0)] + c[("top", 0)] == 200


minimal_tree = newick.loads("(A:2,B:2):1;")[0]

minimal_gml = """graph [
  node [
    id 0
    label "left"
  ]
  node [
    id 1
    label "right"
  ]
  node [
    id 2
    label "off"
  ]
  edge [
    source 0
    target 1
    w 2
  ]
]"""
