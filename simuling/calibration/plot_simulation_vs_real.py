#!/usr/bin/env python

"""Plot simulation results vs. real-world data.

Plot the simulated shared vocabulary proportions between languages on
a tree on top of the real proportions.

"""

import itertools

import sys
import os.path
import argparse

import matplotlib.pyplot as plt

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

    realdata = cached_realdata(args.realdata)
    for pair in args.exclude:
        try:
            first, second = sorted(pair.split("-"))
            realdata.pop((first, second), None)
        except ValueError:
            for i in list(realdata):
                if pair in i:
                    realdata.pop(i)
    print("point", "error",
          *["'{:}-{:}'".format(n1, n2) for n1, n2 in realdata], sep="\t")
    print("real", "0", *realdata.values(), sep="\t")

    names = sorted(realdata, key=realdata.get)
    x = [realdata[n] for n in names]

    plt.plot(x, x, "--", c="0.5")

    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(names)

    parameters = []
    errors = []
    colors = {}
    for sim in args.simulationdata:
        try:
            p = float(os.path.basename(sim.name).split("_")[1])
        except (AttributeError, TypeError):
            p = float("nan")

        scores = {}
        squared_error = 0
        for (l1, vocabulary1), (l2, vocabulary2) in (
                itertools.combinations(read_wordlist(
                    sim, semantics=None, all_languages=True).items(), 2)):
            # Normalize the key, that is, the pair (l1, l2)
            if l1 > l2:
                l1, l2 = l2, l1
            score = shared_vocabulary(vocabulary1, vocabulary2)
            try:
                error = (realdata[l1, l2] - score)
                scores[l1, l2] = score
            except KeyError:
                continue
            squared_error += error ** 2

        y = [scores.get(n) for n in names]
        if p in colors:
            plt.plot(x, y, "-", c=colors[p])
        else:
            colors[p] = plt.plot(x, y, "-", label=p)[0]._color

        print(sim.name, p, squared_error, *y, sep="\t")
        try:
            mean_squared_error = squared_error / len(scores)
            errors.append(mean_squared_error)
            parameters.append(p)
        except ZeroDivisionError:
            continue

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
