import networkx

import numpy
import bisect


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
        weights = numpy.cumsum([v['weight']
                                for m, v in meanings.items()
                                if v['weight'] > 0])
        meanings = [m
                    for m, v in meanings.items()
                    if v['weight'] > 0]
        x = bisect.bisect(weights,
                          numpy.random.random()*weights[-1])
        return meanings[x]

    def enforce(self, message, context, value=1):
        try:
            edge = self.vocabulary[message][context]
        except KeyError as e:
            self.vocabulary.add_edge(message, context, {'weight': 0})
            edge = self.vocabulary[message][context]
        edge['weight'] += value

    def devalue(self, message, context):
        self.enforce(message, context, -1)

    def hear(self, message, context, desired):
        if context is None:
            try:
                meanings = self.vocabulary[message]
                m = self.guess(meanings)
            except (KeyError, IndexError):
                m = self.guess({i: {'weight': len(self.concept_network[i])}
                                for i in self.concept_network.nodes()})
            if m == desired:
                self.enforce(message, m)
            else:
                self.devalue(message, m)
        else:
            self.enforce(message, context)

    def speak(self, meaning, random=numpy.random):
        if random.random() < self.p_invent:
            # Random error leads to inventing a new word
            return "{:d}-{:d}".format(meaning, random.choice(self.W))
        else:
            polysemies = self.vocabulary[meaning]
            if polysemies:
                # There are words attached to this meaning
                return self.guess(polysemies)
            else:
                return "{:d}-{:d}".format(meaning, random.choice(self.W))
