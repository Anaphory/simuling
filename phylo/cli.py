import random
import lingpy
from collections import defaultdict
from .phylo import Phylogeny


def run(times=100, signs=1000, fields=50,
        taxa=list('abcdefghijklmnopqrst'.upper()),
        change_range=2000,
        change_min=1900,
        basic_list=list(range(200))):
    """
    Run one phylo-simulation.
    """
    # print('[i] analyzing setting {0}'.format(i+1))
    concept2field = defaultdict(set)
    for c in range(signs):
        concept2field[random.randint(0, fields-1)].add(c)
    related_concepts = {}
    for field in concept2field.values():
        for concept in field:
            related_concepts[concept] = field - {concept}

    dists_nn, dists_upgma, dists_random = [], [], []
    for i in range(times):
        phy = Phylogeny(
            related_concepts,
            basic=basic_list,
            tree=lingpy.basic.tree.Tree(
                lingpy.basic.tree.random_tree(
                    taxa, branch_lengths=False)),
            change_range=(change_min, change_range))

        phy.simulate()

        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining
        dataframe, columns = phy.collect_word_list()
        D = {index+1: list(row) for index, row in enumerate(dataframe)}
        D[0] = columns

        wl = lingpy.basic.Wordlist(D)

        print(phy.tree)
        wl.calculate('diversity', ref='cogid')

        wl.calculate('tree', ref='cogid', tree_calc='neighbor')
        t2 = lingpy.upgma(wl.distances, wl.taxa)

        d_nn = phy.tree.get_distance(wl.tree, distance='rf')
        d_upgma = phy.tree.get_distance(t2, distance='rf')
        d_random = phy.tree.get_distance(
            lingpy.basic.tree.Tree(lingpy.basic.tree.random_tree(taxa)),
            distance='rf')
        dists_nn += [d_nn]
        dists_upgma += [d_upgma]
        dists_random += [d_random]

        adist = sum([sum(x) for x in wl.distances]) / (len(wl.distances) ** 2)
        print(
            "[i] Generated tree {}.".format(i),
            "The reconstructed trees have rf-distances",
            "{:.2f} (NN: {:})".format(d_nn, wl.tree),
            "{:.2f} (UPGMA: {:})".format(d_upgma, t2),
            "{:.2f} (random)".format(d_random),
            "to the original tree (adist: {:.2f}, "
            "counterparts: {:d}, diversity: {:.2f}).".format(
                adist, len(dataframe), wl.diversity),
            sep="\n    ")
    print('Average distances to true tree:')
    print('Neighbor: {0:.2f}'.format(sum(dists_nn) / len(dists_nn)))
    print('UGPMA:    {0:.2f}'.format(sum(dists_upgma) / len(dists_upgma)))
    print('Random:   {0:.2f}'.format(sum(dists_random) / len(dists_random)))
