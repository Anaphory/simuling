import networkx

import numpy
import bisect


def weighted_choice(frequencies, weight=lambda v: v['weight']):
    weights = numpy.cumsum([weight(v)
                            for m, v in frequencies.items()
                            if weight(v) > 0])
    frequencies = [m
                   for m, v in frequencies.items()
                   if weight(v) > 0]
    x = bisect.bisect(weights,
                      numpy.random.random()*weights[-1])
    return frequencies[x]


class Speaker (object):
    """A single speaker agent in a LanguageForwardSimulation."""
    W = range(10000)
    """ The set of possible different words """

    def __init__(self):
        self.concept_network = networkx.krackhardt_kite_graph()
        self.vocabulary = networkx.Graph()
        self.vocabulary.add_nodes_from(self.concept_network)

        self.p_invent = 0

    def guess(self, meanings):
        weighted_choice(meanings)

    def strengthen(self, message, context, value=1):
        try:
            edge = self.vocabulary[message][context]
        except KeyError:
            self.vocabulary.add_edge(message, context, {'weight': 0})
            edge = self.vocabulary[message][context]
        edge['weight'] += value

    def weaken(self, message, context):
        self.strengthen(message, context, -1)

    def hear(self, message, context, desired):
        if context is None:
            try:
                meanings = self.vocabulary[message]
                m = self.guess(meanings)
            except (KeyError, IndexError):
                m = self.guess({i: {'weight': len(self.concept_network[i])}
                                for i in self.concept_network.nodes()})
            if m == desired:
                self.strengthen(message, m)
            else:
                self.weaken(message, m)
        else:
            self.strengthen(message, context)

    def speak(self, meaning, listener, random=numpy.random):
        if random.random() < self.p_invent:
            # Random error leads to effectively inventing a new word
            return "{:d}-{:d}".format(meaning, random.choice(self.W))
        else:
            polysemies = self.vocabulary[meaning]
            if polysemies:
                # There are words attached to this meaning
                return weighted_choice(polysemies)
            else:
                return "{:d}-{:d}".format(meaning, random.choice(self.W))

"""The `hear` and `speak` methods as they currently are contain no
incentives to have anything but a 1:1 relation between concepts and
words. This can be mitigated by (a) production / transmission /
comprehension errors, (b) modelling word complexity, (c) making
understanding semi-continuous for slightly wrong concepts, (d) asking
to communicate the distinction between concepts instead of one
specific concept, (e) building words from other words, (f) an explicit
limit on vocabulary, or some other model addition, or some variations
thereof, or some combinations thereof.

(a) we should be able to find in the psycholinguistics literature

(b) depends on (a) or (e) – log complexity sounds reasonable – and is
    an alternative to (f)

(c) would tie into (a) from the side of the listener, not the speaker

(d) would work best with (f) or (b) or (a)

(e) needs (b) or (f)

(f) is an alternative to (b) that would be simpler to implement, but
    that naïvely – without any other model complexification – won't be
    able to produce a realistic model.
"""
