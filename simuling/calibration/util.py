#!/usr/bin/env python

import os
import json
import csv

from .compare_simulation_with_data import (
    read_cldf,
    estimate_normal_distribution,
    normal_likelihood,
    pairwise_shared_vocabulary)


def simulate_and_write(tree, sample_threshold, n_sim=3, root=None,
                       **parameters):
    """Simulate evolution on tree and write results to file.

    Simulate lexical evolution on the tree described by `tree`,
    returning a generator that yields a pandas.DataFrame representing
    a CLDF Wordlist for each of the n_sim different simulations.

    If `root` is specified, start the simulation from that language;
    otherwise, initialize the simulation with a random language.

    Side Effects
    ------------
    Writes a file in the current directory for each generated word list.

    Parameters
    ----------
    tree: newick.Node
    sample_threshold: int
    n_sims: int
    root: simuling.phylo.Language or None

    Other named arguments are passed through to simuling.simulate.simulate

    Yields
    ------
    wordlist: pandas.DataFrame

    """
    for i in range(n_sim):
        filename = "simulation_{:}_{:}.csv".format(parameters["scale"], i)
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerow(("ID", "Language_ID", "Feature_ID", "Value",
                             "Weight", "Cognate_Set", "Concept_CogID"))
            for dataframe in simulate(
                    tree, root=root, **parameters):
                writer.writerows(dataframe)
        yield read_cldf(
            filename, sample_threshold=sample_threshold,
            top_word_only=False)


def run_sims_and_calc_lk(tree, realdata, sample_threshold, n_sim=3,
                         ignore=[], normal=False, root=None, **parameters):
    """Run simulations and calculate their Normal likelihood.

    Run `n` simulations and calculate the likelihood of `realdata`
    under a Normal distribution assumption of pairwise shared vocabulary
    proportions give the results of the simulations.

    """
    if normal:
        normals = estimate_normal_distribution(simulate_and_write(
            tree, sample_threshold=sample_threshold,
            n_sim=n_sim, root=root, **parameters))
        return normal_likelihood(realdata, normals,
                                 ignore=ignore)
    else:
        neg_squared_error = 0
        for simulation in simulate_and_write(
                tree, sample_threshold=sample_threshold, n_sim=n_sim,
                root=root, **parameters):
            for (l1, l2), score in (
                    pairwise_shared_vocabulary(simulation, False)):
                if l1 > l2:
                    l1, l2 = l2, l1
                if (l1, l2) in ignore:
                    continue
                error = (realdata[l1, l2] - score)
                print(l1, l2, score, error)
                neg_squared_error -= error ** 2
        return neg_squared_error / n_sim


def cached_realdata(data):
    try:
        with open(os.path.join(
                os.path.dirname(__file__),
                "pairwise_shared_vocabulary.json")) as realdata_cache:
            realdata = json.load(realdata_cache)
        realdata_cache_filename = realdata.pop("FILENAME")
        if realdata_cache_filename != data.name:
            raise ValueError("Cached filename mismatches data file")
    except (FileNotFoundError, ValueError):
        realdata = {" ".join(pair): score
                    for pair, score in pairwise_shared_vocabulary(
                            read_cldf(data, sample_threshold=None,
                                      top_word_only=False))}
        realdata["FILENAME"] = data.name
        with open(os.path.join(
                os.path.dirname(__file__),
                "pairwise_shared_vocabulary.json"), "w") as realdata_cache:
            json.dump(realdata, realdata_cache)
    return {tuple(key.split()): value for key, value in realdata.items()}
