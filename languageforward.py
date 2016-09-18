#!/usr/bin/env python

import networkx
import json
import sys
import random


class Speaker (object):
    """A single speaker agent in a LanguageForwardSimulation."""
    def __init__(self):
        ...


class LanguageForwardSimulation (object):
    """Object that encompasses the simulation.

    A LanguageForwardSimulation represents a forward-time stochastic
    simulation of an evolving population of speakers.
    """
    def __init__(self, population_graph, critical_period, seed=0):
        self.population_graph = population_graph.copy()
        self.seed = seed
        for node in self.population_graph.nodes():
            self.population_graph.node[node]["speaker"] = Speaker()
        self.random = random.Random(self.seed)
        self.critical_period = critical_period

    def random_speaker(self):
        return self.random.choice(self.population_graph.nodes())

    def communication(self, speakers, learner):
        # This is mostly a static method – we could in theory be more
        # object-oriented and derive the speakers from knowing the
        # learner, or be more static and also pass a randomizer. The
        # current compromise is not optimal.
        ...

    def run(self, time_steps):
        for i in range(time_steps):
            die = self.random_speaker()
            self.population_graph.node[die]["speaker"] = child = Speaker()
            for t in range(self.critical_period):
                self.communication(self.population_graph[die], child)


if __name__ == "__main__":
    options = json.load(open(sys.argv[1]))

    seed = options.get("seed", 0)
    """ randomizer seed used for the simulation """

    population_graph = options["population_graph"]
    if population_graph == 'krackhardt':
        population = networkx.krackhardt_kite_graph()
    else:
        raise ValueError("Graph model {:s} not recognized.".format(
            population_graph))

    t = options.get("critical_period", 1)

    simulation = LanguageForwardSimulation(population, t, seed)
    simulation.run(options["time_steps"])

    with open("Data/population", 'w') as output:
        print(simulation.population_graph.edges(), file=output)
