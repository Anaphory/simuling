import lingpy
from .phylo import Phylogeny
from .helpers import semantic_width


def basic_vocabulary_sampler_of_size(n):
    n = int(n)
    return ("b{:d}".format(n),
            lambda language: language.basic_vocabulary(range(n)))


def basic_vocabulary_sampler_from(string_concepts):
    concepts = []
    for entry in concepts:
        try:
            concepts.append(int(entry))
        except ValueError:
            concepts.append(entry)
    return ("b{:}{:d}".format(concepts[0], len(concepts)),
            lambda language: language.basic_vocabulary(concepts))


def run(times=100,
        related_concepts={i: range(2000) for i in range(2000)},
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
