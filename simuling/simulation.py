#!/usr/bin/env python
"""Simulate lexical evolution based on gradual semantic shift.

"""

import bisect
import hashlib
import collections
import numpy.random

import time
import multiprocessing as mp

import networkx


def constant_zero():
    """lambda: 0

    A useful function for defaultdicts, which we need a name for in case of
    pickling.

    """
    return 0


# We need pickle-able functions for multiprocessing, so define this as named
# function.
def square(x):
    """Square a number."""
    return x**2


class SemanticNetwork (networkx.Graph):
    """A network describing relations between concepts.

    In addition to usual graph methods, the semantic network provides
    easy generation of random concepts.

    """
    def __init__(self, *args, neighbor_factor=0.004, **kwargs):
        super().__init__(*args, **kwargs)
        self.neighbor_factor = neighbor_factor

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
        except (KeyError, AttributeError):
            raw_weight = 1
        return self.neighbor_factor * raw_weight

    def concept_weight(self, concept):
        return len(self[concept]) ** 2

    def random(self, random=numpy.random):
        try:
            max_heap = self._heap[-1]
        except AttributeError:
            self._heap = []
            max_heap = 0
            for concept in self.nodes():
                max_heap += self.concept_weight(concept)
                self._heap.append(max_heap)
        index = bisect.bisect(self._heap,
                              random.rand() * max_heap)
        return list(self.nodes())[index]


class SemanticNetworkWithConceptWeight (SemanticNetwork):
    def __init__(self, *args, concept_weight=square, **kwargs):
        super().__init__(*args, **kwargs)
        self._concept_weight = concept_weight

    def concept_weight(self, concept):
        return self._concept_weight(len(self[concept]))


class WeightedBipartiteGraph (dict):
    """A weighted, bipartite graph

    This is the general case of the objects we use to implement
    languages

    """
    def __missing__(self, key):
        self[key] = collections.defaultdict(constant_zero)
        return self[key]

    def add_edge(self, left, right, weight):
        self[left][right] = weight


class Language (WeightedBipartiteGraph):
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
        for s_concept, s_weight in sorted(
                self.weighted_neighbors(concept).items()):
            for word, weight in sorted(self[s_concept].items()):
                if weight > 0:
                    score.setdefault(word, 0)
                    score[word] += weight * s_weight
        return score

    def random_edge(self, random=numpy.random):
        weights = []
        edges = []
        max_weight = 0
        for concept, words in self.items():
            for word, weight in words.items():
                if weight > 0:
                    edges.append((concept, word))
                    max_weight += weight
                    weights.append(max_weight)
        index = bisect.bisect(weights, random.rand() * max_weight)
        return edges[index]

    def step(self, random=numpy.random):
        # Choose v_0
        concept_1 = self.semantics.random(random=random)
        # Choose v_1
        concept_2 = self.semantics.random(random=random)
        while concept_1 == concept_2:
            concept_2 = self.semantics.random(random=random)
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
            new_word = random.randint(2 ** 40)
            self.add_edge(concept_1, new_word, 1)
        # Generate R_1
        words_for_c2_only = set(neighbors_2) - set(neighbors_1)
        # Adapt the language
        if words_for_c2_only:
            incumbent = max(words_for_c2_only, key=neighbors_2.get)
            self[concept_2][incumbent] += 1
        else:
            new_word = random.randint(2 ** 40)
            self.add_edge(concept_2, new_word, 1)

        # Reduce confusing word.
        all_neighbors = self.weighted_neighbors(concept_1)
        for neighbor, wt in self.weighted_neighbors(concept_2).items():
            all_neighbors[neighbor] = all_neighbors.get(neighbor, 0) + wt

        confusing_weight = 0
        for word, weight in neighbors_1.items():
            if word in neighbors_2:
                for target, wt in all_neighbors.items():
                    weight = self[target].get(word, 0) * wt
                    if weight > confusing_weight:
                        confusing_word = word
                        confusing_meaning = target
                        confusing_weight = weight
        if confusing_weight:
            self[confusing_meaning][confusing_word] -= 1
            if self[confusing_meaning][confusing_word] <= 0:
                del self[confusing_meaning][confusing_word]
        else:
            concept, word = self.random_edge(random=random)
            self[concept][word] -= 1
            if self[concept][word] <= 0:
                del self[concept][word]

        # Remove a unit of weight.
        concept, word = self.random_edge(random=random)
        self[concept][word] -= 1
        if self[concept][word] <= 0:
            del self[concept][word]

    def __str__(self):
        return ",\n".join([
            "{:}: {{{:}}}".format(
                c,
                ", ".join(
                    ["{:}: {:}".format(w, float(wt))
                     for w, wt in sorted(ws.items())
                     if wt > 0]))
            for c, ws in sorted(self.items())
            if ws])

    def copy(self):
        return Language(
            {concept: collections.defaultdict(
                constant_zero,
                {word: weight
                 for word, weight in words.items()})
             for concept, words in self.items()},
            self.semantics)

    def write(self, name, writer):
        for concept, words in self.items():
            for word, weight in words.items():
                if weight:
                    writer.writerow([
                        name, concept, word, weight])


def local_seed(node, raw_seed):
    """Given a Node object and a raw seed, calculate a node-specific seed.

    Currently, this function uses the node's name, so for equal raw seeds, the
    local seeds of anonymous nodes will be identical.

    """
    name_hash = int(hashlib.sha256(
        (node.name or "").encode("utf-8")).hexdigest(), 16)
    return (name_hash + raw_seed) % 2**32


def simulate(phylogeny, language,
             seed=0, writer=None):
    """Run a simulation of a root language down a phylogeny."""
    random = numpy.random.RandomState(local_seed(phylogeny, seed))
    for i in range(int(phylogeny.length)):
        language.step(random=random)

    if phylogeny.name:
        if writer:
            language.write(phylogeny.name, writer)
        yield (phylogeny.name, language)
    for c, child in enumerate(phylogeny.descendants):
        for (name, l) in simulate(child, language.copy(),
                                  seed=seed):
            if writer:
                language.write(name, writer)
            yield (name, l)


def walk_depth_order(tree, root_depth=0):
    """Walk a tree in depth order, highest nodes first.

    >>> from newick import loads
    >>> import simuling.simulation
    >>> t = lambda x: loads(x)[0]
    >>> intermingled = ("((((A:1.9,B:1.8)K:5,(C:4.7,D:4.6)N:2)P:1,(E:2.5,"
    ... "F:2.4)L:5)Q:2,((G:5.3,H:5.2)O:3,(I:3.1,J:3.0)M:5)R:1)S;")
    >>> list(simuling.simulation.walk_depth_order(t(intermingled)))
    [(Node("S"), 0), (Node("R"), 1.0), (Node("Q"), 2.0), (Node("P"), 3.0),\
 (Node("O"), 4.0), (Node("N"), 5.0), (Node("M"), 6.0), (Node("L"), 7.0),\
 (Node("K"), 8.0), (Node("J"), 9.0), (Node("I"), 9.1), (Node("H"), 9.2),\
 (Node("G"), 9.3), (Node("F"), 9.4), (Node("E"), 9.5), (Node("D"), 9.6),\
 (Node("C"), 9.7), (Node("B"), 9.8), (Node("A"), 9.9)]

    """
    yield tree, root_depth
    walkers = [
        walk_depth_order(descendant, root_depth + descendant.length)
        for descendant in tree.descendants]
    next_ones = [next(w) for w in walkers]
    while next_ones:
        highest = min(range(len(next_ones)),
                      key=lambda i: next_ones[i][1])
        yield next_ones[highest]
        try:
            replacement = next(walkers[highest])
            next_ones[highest] = replacement
        except StopIteration:
            del walkers[highest]
            del next_ones[highest]


class Multiprocess ():
        def __init__(self, n):
            self.n = n
            manager = mp.Manager()
            self.generated_languages = manager.dict()
            self.io_lock = manager.Lock()

        def worker(self, node_with_height):
            node, height = node_with_height
            name = node.name
            if name in self.generated_languages:
                raise ValueError(
                    "Duplicate node name or unnamed node found: {:}".format(
                        name))
            parent = None if node.ancestor is None else node.ancestor.name

            start_from = self.generated_languages.get(parent)
            while not start_from:
                time.sleep(2)
                start_from = self.generated_languages.get(parent)

            random = numpy.random.RandomState(local_seed(node, self.raw_seed))
            end_at = start_from.copy()
            for i in range(int(node.length)):
                end_at.step(random=random)

            self.generated_languages[name] = end_at

            return name, end_at

        def simulate_remainder(self, phylogeny, language=None,
                               seed=0, writer=None):
            """Run a simulation restricted to generating new languages.

            Run a simulation of a root language down a phylogeny, skipping
            nodes that have already been generated.

            This method is similar to the `simulate` method, but useful for
            continuing from an interrupted simulation.

            """
            for name, language in self.generated_languages.items():
                if writer:
                    language.write(name, writer)
                yield name, language
            self.generated_languages[None] = language
            self.raw_seed = seed
            p = mp.Pool(self.n)
            for name, language in p.imap(
                    self.worker,
                    ((node, height)
                     for node, height in walk_depth_order(phylogeny)
                     if node.name not in self.generated_languages)):
                if writer:
                    language.write(name, writer)
                yield name, language

        def simulate(self, phylogeny, language,
                     seed=0, writer=None):
            """Run a simulation of a root language down a phylogeny.

            As opposed to the `simulate` function, this method makes use of
            multiprocessing. The implementation should be equivalent.

            This method tracks languages which have already been generated by
            name, and therefore expects a tree where all nodes are uniquely
            named, and raises ValueError otherwise.

            """
            self.generated_languages[None] = language
            self.raw_seed = seed
            p = mp.Pool(self.n)

            for name, language in p.imap(
                    self.worker, walk_depth_order(phylogeny)):
                if writer:
                    language.write(name, writer)
                yield name, language
