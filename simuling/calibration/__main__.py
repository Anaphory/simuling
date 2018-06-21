#!/usr/bin/env python

"""Iteratively optimize the simulation scale.

Run simulations at various scales of trees and compare them with
real-world data to find the best scale between tree and simulation
steps.

"""

import itertools

import os
import argparse
import tempfile
from clldutils.path import Path

import csvw
import newick

from ..cli import argparser as basic_argparser, run_and_write, prepare

from .util import cached_realdata, shared_vocabulary


def mean(x):
    x = list(x)
    return sum(x)/len(x)


def argparser():
    """Parse command line arguments."""
    parser = basic_argparser()
    calibration = parser.add_argument_group("Calibration")
    calibration.add_argument(
        "--realdata",
        default=open(os.path.join(os.path.dirname(__file__),
                                  "beijingdaxue1964.csv")),
        type=argparse.FileType("r"),
        help="Word list from real life")
    calibration.add_argument(
        "--minscale",
        type=float,
        default=1,
        help="The minimum scale to use")
    calibration.add_argument(
        "--maxscale",
        type=float,
        default=200,
        help="The maximum scale to use")
    calibration.add_argument(
        "--sims",
        type=int,
        default=3,
        help="How many simulations to run for each scale")
    # FIXME: Instead, override the output option
    calibration.add_argument(
        "--dir", "--directory",
        default=tempfile.mkdtemp(prefix="calibrate"),
        help="Write simulation results to this directory")
    calibration.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="""Ignore these languages or pairs of languages.
        Pairs are separated by colons (":").
        For example --ignore Chaozou:Xiamen""")
    calibration.add_argument(
        "--threshold", "--sample-threshold",
        default=4,
        help="Weight threshold to sample a word")
    parser._option_string_actions["--output"].type = Path
    parser._option_string_actions["--output"].default = Path()
    parser._option_string_actions["--tree"].default = (
        Path(__file__).parent / "dated.tre")
    return parser


def scaled_copy_of(newick_tree, scale):
    root = newick.Node(
        name=newick_tree.name,
        length=str(float(newick_tree.length) * scale))
    for descendant in newick_tree.descendants:
        scaled_copy = scaled_copy_of(descendant, scale)
        root.add_descendant(scaled_copy)
    return root


def main():
    """Run the CLI."""
    parser = argparser()
    args = prepare(parser)
    path = args.output
    os.chdir(str(path))

    raw_seed = args.seed

    scores = {}
    lower = args.minscale
    upper = args.maxscale

    realdata = cached_realdata(args.realdata)

    ignore_pairs = set()
    ignore_singletons = set()
    if args.ignore:
        for i in args.ignore:
            try:
                l1, l2 = i.split(":")
                ignore_pairs.add((l1, l2) if l1 < l2 else (l2, l1))
            except ValueError:
                ignore_singletons.add(i)

    phylogeny = args.phylogeny
    root_language = args.root_language_data

    with csvw.UnicodeWriter(
            Path("shared_vocabularies.csv").open("w")) as writer:
        writer.writerow(["data", "scale", "error"] +
                        ["{:}:{:}".format(l1, l2) for l1, l2 in realdata])
        writer.writerow(["", "", ""] + list(realdata.values()))

        def simulate_scale(scale, seed):
            args.phylogeny = scaled_copy_of(phylogeny, scale)
            args.tree = args.phylogeny.newick
            args.output = "calibration_{:f}_{:d}.csv".format(scale, seed)
            args.seed = raw_seed + seed
            args.root_language_data = root_language.copy()

            squared_error = 0
            for (l1, vocabulary1), (l2, vocabulary2) in (
                    itertools.combinations(run_and_write(args), 2)):
                # Normalize the key, that is, the pair (l1, l2)
                if l1 > l2:
                    l1, l2 = l2, l1
                if (((l1, l2) in ignore_pairs or
                     l1 in ignore_singletons or
                     l2 in ignore_singletons)):
                    continue
                score = shared_vocabulary(vocabulary1, vocabulary2)
                try:
                    error = (realdata[l1, l2] - score)
                    scores[l1, l2] = score
                except KeyError:
                    continue
                squared_error += error ** 2

            writer.writerow([
                args.output,
                scale,
                squared_error] + [
                    scores[l1, l2] for l1, l2 in realdata])
            return squared_error

        sq_errors = {
            lower: mean(simulate_scale(lower, seed)
                        for seed in range(args.sims)),
            upper: mean(simulate_scale(upper, seed)
                        for seed in range(args.sims))}

        try:
            # Take steps that are between the upper and lower scaling factor
            # (geometrically evenly spaced, but that should not be important).
            # As long as the two intermediate spots match the original data
            # better than the border points, and the borders are more than 0.1%
            # different, try to find a better fit by narrowing the distance
            # between the borders, taking the middle points as new borders.
            while upper / lower > 1.001:
                for scale in [
                        (lower**2 * upper) ** (1 / 3),
                        (lower * upper**2) ** (1 / 3)]:
                    sq_errors[scale] = mean(
                        simulate_scale(scale, seed)
                        for seed in range(args.sims))
                    if ((sq_errors[scale] > sq_errors[lower] and
                         sq_errors[scale] > sq_errors[upper])):
                        raise StopIteration

            min_error_at = max(sq_errors, key=sq_errors.get)
            try:
                upper = min(i for i in sq_errors if i > min_error_at)
            except ValueError:
                pass
            try:
                lower = max(i for i in sq_errors if i < min_error_at)
            except ValueError:
                pass

        except (StopIteration, KeyboardInterrupt):
            pass

    print("Simulation likelihoods:")
    for x in sorted(sq_errors):
        print("{:13f} {:13f}".format(x, sq_errors[x]))


if __name__ == '__main__':
    main()
