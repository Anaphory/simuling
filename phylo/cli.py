import random
import lingpy
from collections import defaultdict
from .phylo import Phylogeny
from .helpers import semantic_width


def basic_vocabulary_sampler_of_size(n):
    n = int(n)
    return ("b{:d}".format(n),
            lambda language: language.basic_vocabulary(range(n)))


def run(times=100, signs=1000, fields=50,
        taxa=list('abcdefghijklmnopqrst'.upper()),
        change_range=20000,
        change_min=15000,
        wordlist_filename=None,
        tree_filename=None,
        samplers=[basic_vocabulary_sampler_of_size(200)],
        p_lose=0.5,
        p_gain=0.4,
        p_new=0.1):
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

    for i in range(times):
        phy = Phylogeny(
            related_concepts,
            basic=[],
            tree=lingpy.basic.tree.Tree(
                lingpy.basic.tree.random_tree(
                    taxa, branch_lengths=False)),
            change_range=(change_min, change_range))

        phy.simulate(
            p_lose=p_lose,
            p_gain=p_gain,
            p_new=p_new)

        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining

        print(phy.tree)
        if tree_filename:
            with open("{:}-{:d}.tre".format(
                        tree_filename, i), "w") as tree_file:
                tree_file.write(phy.tree.getNewick())
        for sampler_name, sampler in samplers:
            dataframe, columns = phy.collect_word_list(sampler)
            D = {index+1: list(row) for index, row in enumerate(dataframe)}
            print(len(D))
            D[0] = columns

            wl = lingpy.basic.Wordlist(D)
            if wordlist_filename:
                wl.output(
                    "tsv",
                    filename="{:}-{:}-{:d}".format(
                        wordlist_filename,
                        sampler_name,
                        i))

            print('Concepts per cognate sets: {0:.2f}'.format(
                semantic_width(wl, 'ipa')))
            wl.calculate('diversity', ref='cogid')
            print('Wordlist diversity: {0:.2f}'.format(
                wl.diversity))

