from phylo.phylo import Phylogeny
from collections import defaultdict
import random
import lingpy


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
            tree = lingpy.basic.tree.Tree(
                lingpy.basic.tree.random_tree(
                    taxa, branch_lengths=False)))

        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining
        dataframe, columns = phy.collect_word_list(basic=basic_list)
        D = {index+1: list(row) for index, row in enumerate(dataframe)}
        D[0] = columns

        wl = lingpy.basic.Wordlist(D)

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
            "{:.2f} (NN)".format(d_nn),
            "{:.2f} (UPGMA)".format(d_upgma),
            "{:.2f} (random)".format(d_random),
            "to the original tree (adist: {:.2f}, counterparts: {:d}, diversity: {:.2f}).".format(
                adist, len(dataframe), wl.diversity),
            sep="\n    ")
    print('Average distances to true tree:')
    print('Neighbor: {0:.2f}'.format(sum(dists_nn) / len(dists_nn)))
    print('UGPMA:    {0:.2f}'.format(sum(dists_upgma) / len(dists_upgma)))
    print('Random:   {0:.2f}'.format(sum(dists_random) / len(dists_random)))


def parse_dash(dash, datatype, args, default):
    if '-'+dash in args:
        return datatype(args[args.index('-'+dash)+1])
    return default


def main():

    from sys import argv

    times = parse_dash('t', int, argv, 100)
    cmax = parse_dash('-max', int, argv, 2000)
    cmin = parse_dash('-min', int, argv, 1900)
    signs = parse_dash('s', int, argv, 1000)
    fields = parse_dash('f', int, argv, 50)
    taxa = parse_dash(
            'l',
            lambda x: list(x.upper),
            argv,
            list('abcdefghijklmn'.upper())
            )
    basic = parse_dash('b', lambda x: list(range(x)), argv, list(range(200)))

    if 'run' in argv:
        run(times=times, signs=signs, fields=fields, taxa=taxa,
            change_range=cmax, change_min=cmin, basic_list=basic)
