#!/usr/bin/env python

from ..phylo.simulate import simulate, write_to_file


from .compare_simulation_with_data import (
    read_cldf,
    estimate_normal_distribution,
    normal_likelihood,
    pairwise_shared_vocabulary)


def simulate_and_write(tree, features, related_concepts, scale=1,
                       n_sim=3, initial_weight=100,
                       related_concepts_edge_weight=lambda x: x,
                       root=None):
    """Simulate evolution on tree and write results to file."""
    for i in range(n_sim):
        columns, dataframe = simulate(
            tree, related_concepts, initial_weight=lambda: initial_weight,
            related_concepts_edge_weight=related_concepts_edge_weight,
            scale=scale, verbose=True, root=root, tips_only=False)
        filename = "simulation_{:}_{:}.csv".format(scale, i)
        with open(filename, "w") as f:
            write_to_file(columns, dataframe, f)
        yield read_cldf(filename, features=features)


def run_sims_and_calc_lk(tree, realdata, features, related_concepts,
                         scale=1, n_sim=3, initial_weight=6,
                         related_concepts_edge_weight=lambda x: x,
                         ignore=[], normal=False, root=None):
    """Run simulations and calculate their Normal likelihood.

    Run `n` simulations and calculate the likelihood of `realdata`
    under a Normal distribution assumption of pairwise shared vocabulary
    proportions give the results of the simulations.

    """
    if normal:
        normals = estimate_normal_distribution(simulate_and_write(
            tree, features=features, related_concepts=related_concepts,
            related_concepts_edge_weight=related_concepts_edge_weight,
            scale=scale, n_sim=n_sim, root=root))
        return normal_likelihood(realdata, normals,
                                 ignore=ignore)
    else:
        neg_squared_error = 0
        for simulation in simulate_and_write(
                tree, features=features, related_concepts=related_concepts,
                related_concepts_edge_weight=related_concepts_edge_weight,
                scale=scale, n_sim=n_sim, root=root):
            for (l1, l2), score in (
                    pairwise_shared_vocabulary(simulation, False)):
                if l1 > l2:
                    l1, l2 = l2, l1
                if (l1, l2) in ignore:
                    continue
                error = (realdata[l1, l2] - score) ** 2
                print(l1, l2, score, error)
                neg_squared_error -= error
        return neg_squared_error/n_sim
