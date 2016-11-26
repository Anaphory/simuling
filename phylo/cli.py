import csv
import lingpy
from .phylo import Phylogeny
from .helpers import semantic_width


def basic_vocabulary_sampler(strings):
    concepts = []
    for entry in strings:
        try:
            concepts.append(int(entry))
        except ValueError:
            concepts.append(entry)
    if type(strings) == range:
        name = "b{:d}".format(len(strings))
    else:
        name = "b{:}{:d}".format(concepts[0], len(concepts))
    return (name,
            lambda language: language.basic_vocabulary(concepts))


def run(times=100,
        related_concepts={i: range(2000) for i in range(2000)},
        taxa=list('abcdefghijklmnopqrst'.upper()),
        change_range=20000,
        change_min=15000,
        wordlist_filename=None,
        tree_filename=None,
        samplers=[basic_vocabulary_sampler(range(200))],
        p_lose=0.5,
        p_gain=0.4,
        p_new=0.1):
    """
    Run one phylo-simulation.
    """
    if False:
        phy = Phylogeny(
            related_concepts,
            basic=[],
            tree=lingpy.basic.tree.Tree(newick),
            change_range=(change_min, change_range))

        phy.simulate(
            p_lose=p_lose,
            p_gain=p_gain,
            p_new=p_new)

        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining

        for sampler_name, sampler in samplers:
            dataframe, columns = phy.collect_word_list(sampler)
            if sampler_name:
                filename = "{:}-{:}-{:d}.tsv".format(
                    wordlist_filename,
                    sampler_name,
                    i)
            else:
                filename = "{:}-{:d}.tsv".format(
                    wordlist_filename,
                    i)
            with open(filename, "w") as wordlist_file:
                writer = csv.writer(wordlist_file, 'excel-tab')
                writer.writerow(columns)
                writer.writerows(dataframe)
