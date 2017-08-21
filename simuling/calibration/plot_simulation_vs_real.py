#!/usr/bin/env python

"""Plot simulation results vs. real-world data.

Plot the simulated shared vocabulary proportions between languages on
a tree on top of the real proportions.

"""

import bisect

import matplotlib.pyplot as plt

import os
import sys
import argparse

from . import compare_simulation_with_data
from .compare_simulation_with_data import (
    read_cldf, pairwise_shared_vocabulary)


def ordered_pairwise_shared_vocabulary(data):
    """Get ordered pairwise shared vocabulary of languages.

    For every pair of languages in `data`, calculate the proportion of
    features where they share values (usually the shared vocabulary
    according to a word list).

    Returns:

    proportions – list of floats: The pairwise proportions of shared
    vocabulary, in ascending order.

    pairs – list of pairs: The language pairs, in the corresponding
    order.

    """
    proportions = []
    pairs = []
    for (language1, language2), score in (
            pairwise_shared_vocabulary(data, False)):
        i = bisect.bisect(proportions, score)
        proportions.insert(i, score)
        pairs.insert(i, (language1, language2))
    return proportions, pairs


def compatible_pairwise_shared_vocabulary(data, order):
    """Get ordered shared vocabulary of languages in given order.

    For every pair of languages listed in `order`, calculate the
    proportion of shared vocabulary (as given by `data`), and return
    them in precisely that order.

    """
    for language1, language2 in order:
        vocabulary1 = data[data["Language_ID"] == language1]
        vocabulary2 = data[data["Language_ID"] == language2]
        score = compare_simulation_with_data.shared_vocabulary(
            vocabulary1, vocabulary2)
        yield score


def plot_vocabulary(x, names, simulated, axis=None):
    """Plot the simulated data against reference language distances."""
    if axis is None:
        axis = plt.gca()

    y = list(compatible_pairwise_shared_vocabulary(simulated, names))
    axis.plot(x, y)
    return y


def main(args=sys.argv):
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "realdata",
        type=argparse.FileType("r"),
        help="Word list from real life")
    parser.add_argument(
        "simulationdata",
        nargs="*",
        type=argparse.FileType("r"),
        help="Wordlist given by the phylo simulation")
    parser.add_argument(
        "--figure-file",
        help="File to write the figure to")
    parser.add_argument(
        "--error-figure-file",
        help="File to write the error plot to")
    args = parser.parse_args(args)

    x, names = ordered_pairwise_shared_vocabulary(read_cldf(args.realdata))
    print("point", "error", *["'{:}-{:}'".format(n1, n2) for n1, n2 in names],
          sep="\t")
    print("real", "0", *x, sep="\t")
    plt.plot(x, x, "--", c="0.5")

    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(names)

    parameters = []
    errors = []
    for sim in args.simulationdata:
        y = plot_vocabulary(x, names, read_cldf(sim))
        error = (sum([(xi-yi)**2 for xi, yi in zip(x, y)])/len(x))**0.5
        try:
            p = float(os.path.basename(sim.name).split("_")[1])
        except (AttributeError, TypeError):
            p = float("nan")
        parameters.append(p)
        errors.append(error)
        print(sim.name, p, error, *y, sep="\t")

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(6)
        # specify integer or one of preset strings, e.g.
        # tick.label.set_fontsize('x-small')
        tick.label.set_rotation('vertical')

    if args.figure_file:
        plt.savefig(args.figure_file)
    else:
        plt.show()

    plt.figure()

    plt.scatter(parameters, errors)
    if args.figure_file:
        plt.savefig(args.error_figure_file)
    else:
        plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
