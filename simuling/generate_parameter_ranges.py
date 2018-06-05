#!/usr/bin/env python

"""Generate the data to assess simulation robustness.

Run the simulation on a long branch with parameter variation.
"""

import shlex

from .analysis import default_properties
from .cli import concept_weights


initial_weights = [
    "1",
    "6",
    "10",
    "20",
    "30",
    "60",
    "100",
    "200",
    "400",
    "800",
    "uniform(10)",
    "uniform(60)",
    "uniform(199)",
    "geometric(100)",
    "poisson(100)"]

file_id = 1


def new_output_file():
    global file_id
    file_id += 1
    return "long_branch_{:08x}.csv".format(file_id)


def write_parameter_line(updater, arguments=default_properties):
    arguments = arguments.copy()
    arguments.update(updater)
    arguments["--output-file"] = new_output_file()
    print("cat {:} || python3 -m simuling --embed ".format(
        arguments["--output-file"]) + " ".join(
            "{:} {:}".format(argument.replace("_", "-"),
                             shlex.quote(str(value)))
            for argument, value in arguments.items()))


for seed in range(5):
    print("# Seed {:d}".format(seed))
    write_parameter_line({"--seed": seed})

    for initial_weight in initial_weights:
        write_parameter_line({"--weight": initial_weight,
                              "--seed": seed})

    for neighbor_factor in [0., 0.0004, 0.0008, 0.002, 0.004, 0.006, 0.01,
                            0.02, 0.03, 0.04, 0.05]:
        write_parameter_line({"--neighbor-factor": neighbor_factor,
                              "--seed": seed})

    for name in concept_weights:
        write_parameter_line({"--concept-weight": name,
                              "--seed": seed})
