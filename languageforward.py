#!/usr/bin/env python

import networkx
import json
import sys
import random

from speaker import Speaker


class LanguageForwardSimulation (object):
    """Object that encompasses the simulation.

    A LanguageForwardSimulation represents a forward-time stochastic
    simulation of an evolving population of speakers.
    """
    def __init__(self,
                 population_graph, critical_period,
                 p_context=0.5, seed=0, logfile=None):
        self.population_graph = population_graph.copy()
        self.seed = seed
        for node in self.population_graph.nodes():
            self.population_graph.node[node]["speaker"] = Speaker()
        self.random = random.Random(self.seed)
        self.critical_period = critical_period
        self.p_context = p_context
        self.logfile = logfile

    def random_speaker(self):
        return self.random.choice(self.population_graph.nodes())

    def random_speaker_among(self, neighbours):
        return self.population_graph.node[
            self.random.choice(list(neighbours.keys()))]["speaker"]

    def generate_situation(self):
        concept = self.random.randrange(10)
        context = concept if self.random.random() < self.p_context else None
        return concept, context

    def log(self, speaker):
        if self.logfile:
            for f, t in speaker.vocabulary.edge.items():
                if type(f) == int:
                    print(f, t, file=self.logfile)
            print(file=self.logfile)

    def run(self, time_steps):
        for i in range(time_steps):
            die = self.random_speaker()
            self.population_graph.node[die]["speaker"] = child = Speaker()
            for t in range(self.critical_period):
                concept, context = self.generate_situation()
                speaker = self.random_speaker_among(self.population_graph[die])
                child.hear(speaker.speak(concept, child), context, concept)
            self.log(child)


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

    simulation = LanguageForwardSimulation(
        population, t,
        seed=seed, logfile=open("Data/log", 'w'))
    simulation.run(options['time_steps'])
