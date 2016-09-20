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
