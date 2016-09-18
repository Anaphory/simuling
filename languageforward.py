#!/usr/bin/env python

import networkx
import json
import sys


class Speaker (object):
    """A single speaker agent in a LanguageForwardSimulation."""
    def __init__(self):
        ...
    ...


class LanguageForwardSimulation (object):
    """Object that encompasses the simulation.

    A LanguageForwardSimulation represents a forward-time stochastic
    simulation of an evolving population of speakers.
    """
    def __init__(self, population_graph, seed=0):
        self.population_graph = population_graph.copy()
        self.seed = seed
        for node in self.population_graph.nodes():
            self.population_graph.node[node]["speaker"] = Speaker()

    def run(self, time_steps):
        for i in range(time_steps):
            ...

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

    simulation = LanguageForwardSimulation(population, seed)
    simulation.run(options["time_steps"])

    with open("Data/population", 'w') as output:
        print(simulation.population_graph.edges(), file=output)
