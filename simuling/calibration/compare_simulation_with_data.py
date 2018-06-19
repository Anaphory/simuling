#!/usr/bin/env python

"""Compare real word list with simulated word lists.

After running the simulation on a realistic dated tree (with some
scaling of tree branches to years), this script compares the actual
word list with the simulation results.

"""

import pandas
import itertools

import sys
import argparse


def read_cldf(file, features=None, sample_threshold=0, top_word_only=True):
    """Read a CLDF TSV file.

    Read a tsv file as output by the simulation and rename the columns
    such that the cognate IDs become `value`.

    Use features=None for all features, or supply a sequence of feature
    IDs to filter.

    """
    sep = "\t"
    if hasattr(file, 'name') and file.name.endswith("csv"):
        sep = ","
    elif hasattr(file, 'endswith') and file.endswith("csv"):
        sep = ","
    elif hasattr(file, 'seek'):
        ...

    data = pandas.read_csv(file, sep=sep, index_col="ID")
    if "Parameter_ID" in data.columns:
        if "Feature_ID" in data.columns:
            raise ValueError(
                "Two feature id columns: Parameter_ID and Feature_ID!")
        data.columns = ["Feature_ID" if c == "Parameter_ID" else c
                        for c in data.columns]
    if features is None:
        pass
    else:
        include = (data["Feature_ID"] == object())
        for feature in features:
            include |= data["Feature_ID"] == feature
        data = data[include]
    data = data[~pandas.isnull(data["Feature_ID"])]
    if sample_threshold:
        data = data[data["Weight"] > sample_threshold]
    if top_word_only:
        data.sort_values(by="Weight", inplace=True)
        data = data.groupby([
            "Feature_ID", "Language_ID"]).last().reset_index(drop=False)
    return data


def read_lingpy(file, features=None):
    """Read a file in LingPy conventions.

    WARNING: Currently only works for beida-1964.tsv, because it
    assumes specific colums.

    """
    data = pandas.read_csv(file, sep="\t", index_col="ID")
    data.columns = ["Language_ID", "Feature_ID", "Form", "Hanzi", "Value"]
    if features is None:
        pass
    else:
        include = (data["Feature_ID"] == object())
        for feature in features:
            include |= data["Feature_ID"] == feature
        data = data[include]
    return data


def shared_vocabulary(vocab1, vocab2):
    """Calculate the proportion of shared items between two wordlists.

    For the pair of languages which are sampled in `vocab1` and
    `vocab2`, calculate how many cognate-meaning pairs they
    share. Multiple cognates in one meaning slot are counted as
    |C∪D|/|C∩D|, or 1/|C∪D| if one of the meanings is unattested.

    """
    features_present_in_one = set(
        vocab1["Feature_ID"]) | set(vocab2["Feature_ID"])
    score = 0
    for feature in features_present_in_one:
        cognateset1 = set(vocab1["Cognate_Set"][
            vocab1["Feature_ID"] == feature])
        cognateset2 = set(vocab2["Cognate_Set"][
            vocab2["Feature_ID"] == feature])
        score += (len(cognateset1 & cognateset2) /
                  len(cognateset1 | cognateset2))
    return score / len(features_present_in_one)


def pairwise_shared_vocabulary(data, verbose=True):
    """Calculate the proportion of shared vocabulary from the data.

    For every pair of languages, calculate how many cognate-meaning
    pairs they share. Multiple cognates in one meaning slot are
    counted as |C∪D|/|C∩D|, or 1/|C∪D| if one of the meanings is
    unattested.

    """
    for (language1, vocabulary1), (language2, vocabulary2) \
            in itertools.combinations(data.groupby("Language_ID"), 2):
        score = shared_vocabulary(vocabulary1, vocabulary2)
        if verbose:
            print(language1, language2, score)
        yield (language1, language2), score


def estimate_normal_distribution(datasets):
    """Fit normal distribution parameters from a sequence of wordlists.

    Given a sequence of word lists, presumably from simulation,
    calculate the pairwise shared vocabulary proportion for each word
    list and estimate the parameters of the Normal distribution that
    would best explain those proportions.

    """
    import scipy.stats

    proportions = {}
    for data in datasets:
        for pair, value in pairwise_shared_vocabulary(data):
            proportions.setdefault(pair, []).append(value)
    for pair in proportions:
        try:
            parameters = scipy.stats.norm.fit(proportions[pair])
        except scipy.stats._continuous_distns.FitSolverError:
            print(proportions[pair])
            raise
        print(pair, parameters)
        proportions[pair] = parameters
    return proportions


def normal_likelihood(data, normals, ignore=[]):
    """Calculate the likelihood of data from Normal distributions.

    Calculate the logarithm of the likelihood of the pairwise shared
    vocabulary proportions in the word list `data` when assuming all
    of them are independently Normal distributed with α and β as given
    in `normals`.

    """
    import scipy.stats

    loglk = 0
    for pair, value in data.items():
        if pair in ignore:
            continue
        parameters = normals[pair]
        loglk += scipy.stats.norm.logpdf(value, *parameters)
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

    normals = estimate_normal_distribution(map(read_cldf,
                                               args.simulationdata))
    loglk = normal_likelihood(read_lingpy(args.realdata),
                              normals)
    print(loglk)


if __name__ == "__main__":
    main(sys.argv[1:])
