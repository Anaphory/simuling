#!/usr/bin/env python
"""Simulate lexical evolution based on gradual semantic shift.

"""

import bisect
import random
import collections

import newick
import networkx

from pathlib import Path


class SemanticNetwork (networkx.Graph):
    """A network describing relations between concepts.

    In addition to usual graph methods, the semantic network provides
    easy generation of random concepts.

    """
    neighbor_factor = 0.004

    @classmethod
    def load_from_gml(cls, lines, weight_attribute):
        related_concepts = networkx.parse_gml(lines)
        network = cls(related_concepts)
        network.weight_attribute = weight_attribute
        return network

    def edge_weight(self, original_meaning, connected_meaning):
        try:
            edge_properties = self[original_meaning][connected_meaning]
        except KeyError:
            # No such edge.
            return 0
        try:
            raw_weight = edge_properties[self.weight_attribute]
        except KeyError:
            raw_weight = 1
        return self.neighbor_factor * raw_weight

    def concept_weight(self, concept):
        return len(self[concept]) ** 2

    def random(self, random=random):
        try:
            max_heap = self._heap[-1]
        except AttributeError:
            self._heap = []
            max_heap = 0
            for concept in self.nodes():
                max_heap += self.concept_weight(concept)
                self._heap.append(max_heap)
        index = bisect.bisect(self._heap,
                              random.random() * max_heap)
        return self.nodes()[index]


class WeightedBipartiteGraph (dict):
    """A weighted, bipartite graph

    This is the general case of the objects we use to implement
    languages

    """
    def __missing__(self, key):
        self[key] = collections.defaultdict(lambda: 0)
        return self[key]

    def add_edge(self, left, right, weight):
        self[left][right] = weight


class Language (WeightedBipartiteGraph):
    max_word = 0

    def __init__(self, dictionary, semantics):
        super().__init__(dictionary)
        self.semantics = semantics

    def weighted_neighbors(self, concept):
        weights = {
            x: self.semantics.edge_weight(concept, x)
            for x in self.semantics[concept]}
        weights[concept] = 1
        return weights

    def calculate_scores(self, concept):
        score = {}
        for s_concept, s_weight in self.weighted_neighbors(concept).items():
            for word, weight in self[s_concept].items():
                if weight > 0:
                    score.setdefault(word, 0)
                    score[word] += weight * s_weight
        return score

    def random_edge(self, random=random):
        weights = []
        edges = []
        max_weight = 0
        for concept, words in self.items():
            for word, weight in words.items():
                if weight > 0:
                    edges.append((concept, word))
                    max_weight += weight
                    weights.append(max_weight)
        index = bisect.bisect(weights, random.random() * max_weight)
        return edges[index]

    def step(self):
        # Choose v_0
        concept_1 = self.semantics.random()
        # Choose v_1
        concept_2 = self.semantics.random()
        while concept_1 == concept_2:
            concept_2 = self.semantics.random()
        # Calculate scores x_w0 for v_0
        neighbors_1 = self.calculate_scores(concept_1)
        # Calculate scores x_w1 for v_1
        neighbors_2 = self.calculate_scores(concept_2)
        # Generate R_0
        words_for_c1_only = set(neighbors_1) - set(neighbors_2)
        # Adapt the language
        if words_for_c1_only:
            incumbent = max(words_for_c1_only, key=neighbors_1.get)
            self[concept_1][incumbent] += 1
        else:
            self.add_edge(concept_1, Language.max_word, 1)
            Language.max_word += 1
        # Generate R_1
        words_for_c2_only = set(neighbors_2) - set(neighbors_1)
        # Adapt the language
        if words_for_c2_only:
            incumbent = max(words_for_c2_only, key=neighbors_2.get)
            self[concept_2][incumbent] += 1
        else:
            self.add_edge(concept_2, Language.max_word, 1)
            Language.max_word += 1

        # Reduce confusing word.
        all_neighbors = self.weighted_neighbors(concept_1)
        for neighbor, wt in self.weighted_neighbors(concept_2).items():
            all_neighbors[neighbor] = all_neighbors.get(neighbor, 0) + wt

        confusing_weight = 0
        for word, weight in neighbors_1.items():
            if word in neighbors_2:
                for target, wt in all_neighbors.items():
                    weight = self[target][word] * wt
                    if weight > confusing_weight:
                        confusing_word = word
                        confusing_meaning = target
                        confusing_weight = weight
        if confusing_weight:
            self[confusing_meaning][confusing_word] -= 1
            if self[confusing_meaning][confusing_word] <= 0:
                del self[confusing_meaning][confusing_word]
        else:
            concept, word = self.random_edge()
            self[concept][word] -= 1
            if self[concept][word] <= 0:
                del self[concept][word]

        # Remove a unit of weight.
        concept, word = self.random_edge()
        self[concept][word] -= 1
        if self[concept][word] <= 0:
            del self[concept][word]

    def __str__(self):
        return ",\n".join([
            "{:}: {{{:}}}".format(
                c,
                ", ".join(
                    ["{:}: {:}".format(w, wt)
                     for w, wt in ws.items()
                     if wt > 0]))
            for c, ws in self.items()
            if ws])

    def copy(self):
        return Language(
            {concept: collections.defaultdict(
                (lambda: 0),
                {word: weight
                 for word, weight in words.items()})
             for concept, words in self.items()},
            self.semantics)


def simulate(phylogeny, language):
    """Run a simulation of a root language down a phylogeny"""
    if phylogeny.name:
        yield (phylogeny.name, language)
    for i in range(int(phylogeny.length)):
        language.step()
    for child in phylogeny.descendants:
        for (name, language) in simulate(child, language.copy()):
            yield (name, language)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    initialization = parser.add_argument_group(
        "Initializing the root language")
    initialization.add_argument(
        "--wordlist", type=argparse.FileType("r"),
        help="Load the root language from this CLDF Wordlist. (default: Create"
        " a new language with exactly one word for each concept.)")
    initialization.add_argument(
        "--language",
        help="Load this Language_ID from the CLDF Wordlist. (default: The one"
        " referred to in the last line of the table with the Cognateset_IDs.)")
    initialization.add_argument(
        "--weight",
        help="Random distribution to use when initializing the root language,"
        " if no weights are given in the CLDF Wordlist. (default: The"
        " distribution that always returns 100.)")
    parameters = parser.add_argument_group(
        "Simulation parameters")
    parameters.add_argument(
        "--semantic-map", type=argparse.FileType("r"),
        help="The semantic network, given as GML file. (default: CLICS.)")
    parameters.add_argument(
        "--weight-attribute",
        help="The GML edge attribute to be used as edge weight."
        " (default: FamilyWeight.)")
    tree = parser.add_argument_group(
        "Shape of the phylogeny")
    parameters.add_argument(
        "--tree", type=argparse.FileType("r"),
        help="A file containing the phylogenetic trees to be simulated in"
        " Newick format. (default: A single long branch with nodes after"
        " 0, 1, 2, 4, 8, …, 2^20 time steps.)")

    args = parser.parse_args()
    if args.semantic_map:
        semantics = SemanticNetwork.load_from_gml(args.semantic_map,
                                                  args.weight_attribute)
    else:
        semantics = SemanticNetwork.load_from_gml(
            (Path(__file__).absolute().parent.parent /
             "phylo" / "network-3-families.gml").open(),
            args.weight_attribute)
    if args.weight:
        ...
    else:
        def weight():
            return 100
    if args.tree:
        phylogeny = newick.load(args.tree)[0]
    else:
        phylogeny = newick.Node("0")
        parent = phylogeny
        length = 0
        for i in range(21):
            new_length = 2 ** i
            child = newick.Node(
                str(new_length),
                str(new_length - length))
            parent.add_descendant(child)
            parent = child
            length = new_length
    if args.wordlist:
        ...
    else:
        raw_language = {
            concept: collections.defaultdict(
                (lambda: 0), {c: weight()})
            for c, concept in enumerate(semantics)}
        language = Language(raw_language, semantics)
        Language.max_word = len(raw_language)
    print(phylogeny.newick)
    with Path("test.log").open("w") as log:
        print("Language_ID", "Parameter_ID", "Cognateset_ID", "Weight",
              sep="\t", file=log)
    for id, data in simulate(phylogeny, language):
        with Path("test.log").open("a") as log:
            for concept, words in data.items():
                for word, weight in words.items():
                    if weight:
                        print(id, concept, word, weight, sep="\t", file=log)


# Tests
def test_dumb_semantic_loader():
    """Is the default semantic network available?"""
    SemanticNetwork.load_from_gml(
        Path("../phylo/network-3-families.gml").open(),
        "FamilyWeight")


def test_semantic_weight():
    """Does a semantic network have expected edge weights?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    assert s.weight("left", "right") == 2 * 0.004


def test_semantic_concept_weight():
    """Does a semantic network have the expected concept weights?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    assert s.concept_weight("160") == 1 ** 2


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
    lg = Language({"top": collections.defaultdict(lambda: 0, {0: 10})})
    lg.semantics = s
    assert lg.weighted_neigbors("left") == {'right': 0.008, 'left': 1}


def test_language_cs():
    """Does the language calculate the scores correctly?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    lg = Language({"left": collections.defaultdict(lambda: 0, {0: 10})})
    lg.semantics = s
    assert lg.calculate_scores("left") == {0: 10}
    assert lg.calculate_scores("right") == {0: 0.08}


def test_language_re():
    """Does the language provide the right weighted distribution of edges?"""
    s = SemanticNetwork.load_from_gml(minimal_gml.split("\n"), "w")
    lg = Language({"top": collections.defaultdict(lambda: 0, {0: 10}),
                  "left": collections.defaultdict(lambda: 0, {0: 10})})
    lg.semantics = s
    c = collections.Counter()
    for i in range(200):
        c[lg.random_edge()] += 1
    assert c[("right", 0)] == 0
    assert 80 < c[("left", 0)] < 120
    assert c[("left", 0)] + c[("top", 0)] == 200
    print(c)


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
