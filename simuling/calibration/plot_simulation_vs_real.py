#!/usr/bin/env python

"""Plot simulation results vs. real-world data.

Plot the simulated shared vocabulary proportions between languages on
a tree on top of the real proportions.

"""

import bisect

import matplotlib.pyplot as plt

import sys
import argparse

import compare_simulation_with_data
from compare_simulation_with_data import pairwise_shared_vocabulary
from compare_simulation_with_data import read_cldf


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


def plot_vocabularies(real, *simulated):
    """Plot the simulated data against reference language distances."""
    x, names = ordered_pairwise_shared_vocabulary(real)
    print("point", *["'{:}-{:}'".format(n1, n2) for n1, n2 in names],
          sep="\t")
    print("real", *x, sep="\t")
    plt.plot(x, x, "--", c="0.5")
    for d, data in enumerate(simulated):
        y = list(compatible_pairwise_shared_vocabulary(
            data, names))
        print(d, *y, sep="\t")
        plt.plot(x, y)

    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(6)
        # specify integer or one of preset strings, e.g.
        # tick.label.set_fontsize('x-small')
        tick.label.set_rotation('vertical')


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
    args = parser.parse_args(args)

    plot_vocabularies(
        read_cldf(args.realdata),
        *map(read_cldf, args.simulationdata))
    if args.figure_file:
        plt.savefig(args.figure_file)
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
