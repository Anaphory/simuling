#!/usr/bin/env python
"""Simulate lexical evolution based on gradual semantic shift.

"""

import bisect
import collections
import numpy.random as random

import multiprocessing as mp

import networkx


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
        return list(self.nodes())[index]


class SemanticNetworkWithConceptWeight (SemanticNetwork):
    def __init__(self, *args, concept_weight=lambda degree: degree**2,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.concept_weight = lambda concept: concept_weight(
            len(self[concept]))


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

    def write(self, name, writer):
        for concept, words in self.items():
            for word, weight in words.items():
                if weight:
                    writer.writerow([
                        name, concept, word, weight])


def simulate(phylogeny, language, writer=None):
    """Run a simulation of a root language down a phylogeny."""
    if phylogeny.name:
        yield (phylogeny.name, language)
    for i in range(int(phylogeny.length)):
        language.step()
    for child in phylogeny.descendants:
        for (name, language) in simulate(child, language.copy()):
            if writer:
                language.write(name, writer)
            yield (name, language)


def walk_depth_order(tree, root_depth=0):
    """Walk a tree in depth order, highest nodes first.

    >>> from newick import loads
    >>> t = lambda x: newick.loads(x)[0]
    >>> intermingled = "((((A:1.9,B:1.8)K:5,(C:4.7,D:4.6)N:2)P:1,(E:2.5,F:2.4)L:5)Q:2,((G:5.3,H:5.2)O:3,(I:3.1,J:3.0)M:5)R:1)S;"
    >>> list(walk_tree_depth_order(t(intermingled)))
    [(Node("S"), 0), (Node("R"), 1.0), (Node("Q"), 2.0), (Node("P"), 3.0), (Node("O"), 4.0), (Node("N"), 5.0), (Node("M"), 6.0), (Node("L"), 7.0), (Node("K"), 8.0), (Node("J"), 9.0), (Node("I"), 9.1), (Node("H"), 9.2), (Node("G"), 9.3), (Node("F"), 9.4), (Node("E"), 9.5), (Node("D"), 9.6), (Node("C"), 9.7), (Node("B"), 9.8), (Node("A"), 9.9)]

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


def multiprocess_simulate(phylogeny, language, writer=None):
    """Run a simulation of a root language down a phylogeny.

    As opposed to the `simulate` function, this function makes use of
    multiprocessing. The implementation should be equivalent.

    This function expects a tree where all nodes are uniquely named, and raises
    ValueError otherwise.

    """
    with mp.Manager() as manager:
        generated_languages = manager.dict()
        generated_languages[None] = language
        io_lock = manager.Lock()

        def worker(node, height):
            name = node.name
            if name in generated_languages:
                raise ValueError("Duplicate node name or unnamed node found")
            parent = None if node.ancestor is None else node.ancestor.name

            start_from = generated_languages.get(parent)
            while not start_from:
                time.sleep(2)
                start_from = generated_languages.get(parent)

            end_at = start_from.copy()
            for i in range(int(node.length)):
                end_at.step()

            generated_languages[name] = end_at

            if writer:
                io_lock.acquire()
                language.write(name, writer)
                io_lock.release()

            return name, language

        p = multiprocessing.Pool(2)

        for result in p.imap(worker, walk_depth_order(phylogeny)):
            yield result

