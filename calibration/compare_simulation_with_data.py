#!/usr/bin/env python

"""Compare real word list with simulated word lists.

After running the simulation on a realistic dated tree (with some
scaling of tree branches to years), this script compares the actual
word list with the simulation results.

"""

import pandas
import itertools
import scipy.stats

import sys
import argparse


def read_cldf(file):
    """Read a CLDF TSV file.

    Read a tsv file as output by the simulation and rename the columns
    such that the cognate IDs become `value`.

    """
    data = pandas.read_csv(file, sep="\t", index_col="ID")
    data.columns = ["Language_ID", "Feature_ID", "Form", "Weight", "Value",
                    "Concept_CogID"]
    return data


def read_lingpy(file):
    """Read a file in LingPy conventions.

    WARNING: Currently only works for beida-1964.tsv, because it
    assumes specific colums.

    """
    data = pandas.read_csv(file, sep="\t", index_col="ID")
    data.columns = ["Language_ID", "Feature_ID", "Form", "Hanzi", "Value"]
    return data


def pairwise_shared_vocabulary(data, verbose=True):
    """Calculate the proportion of shared vocabulary from the data.

    For every pair of languages, calculate how many cognate-meaning
    pairs they share. Multiple cognates in one meaning slot are
    counted as |C∪D|/|C∩D|, or 1/|C∪D| if one of the meanings is
    unattested.

    """
    for (language1, vocabulary1), (language2, vocabulary2) \
            in itertools.combinations(data.groupby("Language_ID"), 2):
        features_present_in_one = set(
            vocabulary1["Feature_ID"]) | set(vocabulary2["Feature_ID"])
        score = 0
        for feature in features_present_in_one:
            cognateset1 = set(vocabulary1["Value"][
                vocabulary1["Feature_ID"] == feature])
            cognateset2 = set(vocabulary2["Value"][
                vocabulary2["Feature_ID"] == feature])
            if cognateset1 & cognateset2:
                score += (len(cognateset1 & cognateset2)
                          / len(cognateset1 | cognateset2))
            else:
                score += 1 / len(cognateset1 | cognateset2)
        if verbose:
            print(language1, language2, score/len(features_present_in_one))
        yield (language1, language2), score/len(features_present_in_one)


def estimate_beta_distribution(datasets):
    """Fit beta distribution parameters from a sequence of wordlists.

    Given a sequence of word lists, presumably from simulation,
    calculate the pairwise shared vocabulary proportion for each word
    list and estimate the parameters of the Beta distribution that
    would best explain those proportions.

    """
    proportions = {}
    for data in datasets:
        for pair, value in pairwise_shared_vocabulary(data):
            proportions.setdefault(pair, []).append(value)
    for pair in proportions:
        try:
            a, b, _, _ = scipy.stats.beta.fit(proportions[pair],
                                              floc=0, fscale=1)
        except scipy.stats._continuous_distns.FitSolverError:
            print(proportions[pair])
            raise
        proportions[pair] = (a, b)
    return proportions


def beta_likelihood(data, betas):
    """Calculate the likelihood of data from Beta distributions.

    Calculate the logarithm of the likelihood of the pairwise shared
    vocabulary proportions in the word list `data` when assuming all
    of them are independently Beta distributed with α and β as given
    in `betas`.

    """
    loglk = 0
    for pair, value in pairwise_shared_vocabulary(data):
        alpha, beta = betas[pair]
        loglk += scipy.stats.beta.logpdf(value, alpha, beta)
    return loglk


def main(args=sys.argv):
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "realdata",
        type=argparse.FileType("r"),
        help="Word list from real life")
    parser.add_argument(
        "simulationdata",
        nargs="+",
        type=argparse.FileType("r"),
        help="Wordlist given by the phylo simulation")
    args = parser.parse_args(args)

    betas = estimate_beta_distribution(map(read_cldf,
                                           args.simulationdata))
    loglk = beta_likelihood(read_lingpy(args.realdata),
                            betas)
    print(loglk)


if __name__ == "__main__":
    main(sys.argv[1:])
