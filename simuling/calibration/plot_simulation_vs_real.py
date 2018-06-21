#!/usr/bin/env python

"""Plot simulation results vs. real-world data.

Plot the simulated shared vocabulary proportions between languages on
a tree on top of the real proportions.

"""

import matplotlib.pyplot as plt

import sys
import os.path
import argparse

from .util import cached_realdata, shared_vocabulary, read_wordlist


def plot_vocabulary(x, names, simulated, name=None, axis=None):
    """Plot the simulated data against reference language distances."""
    if axis is None:
        axis = plt.gca()

    y = list(shared_vocabulary(simulated, names))
    axis.plot(x, y, label=name, marker="_")
    return y


def main(args=sys.argv):
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "realdata",
        type=argparse.FileType("r"),
        help="Word list from real life")
    # parser.add_argument(
    #     "--no-legend",
    #     default=False,
    #     action='store_true')
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
    parser.add_argument(
        "--exclude", "-x",
        default=[],
        action="append",
        help="language pairs (separated by '-') to ignore")
    args = parser.parse_args(args)

    x, names = cached_realdata(args.realdata)
    for pair in args.exclude:
        first, second = sorted(pair.split("-"))
        try:
            i = names.index((first, second))
            del x[i]
            del names[i]
        except ValueError:
            continue
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
        y = plot_vocabulary(x, names, read_wordlist(sim, sample_threshold=4),
                            name=sim.name)
        error = (sum([(xi-yi)**2 for xi, yi in zip(x, y)])/len(x))**0.5
        try:
            p = float(os.path.basename(sim.name).split("_")[1])
        except (AttributeError, TypeError):
            p = float("nan")
        parameters.append(p)
        errors.append(error)
        print(sim.name, p, error, *y, sep="\t")

    plt.legend()

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
