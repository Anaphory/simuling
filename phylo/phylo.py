import lingpy
import random
import pandas 
import numpy

from .pandas_phylo import Language
class Phylogeny(object):
    """
    The main simulation handler.

    Notes
    -----
    Uses lingpy to get a random tree, uses also the lingpy.Tree class to handle
    the walk along the tree. A parameter "change_range" handles the amount of
    change (say: between 100 and 200 change runs, etc.). Later (this is
    inconsistent!), there's the param "change_min", allowing to set the minimal
    amount of change to happen.
    """

    def __init__(
            self,
            related_concepts,
            tree,
            root=None,
            basic=range(100),
            initial_max_wt=10):
        # distribute fields over concepts
        self.related_concepts = related_concepts
        self.tree = tree

        if root is None:
            self.root = Language(
                self.related_concepts, initial_max_wt)
        else:
            self.root = root
        self.change_range = (500, 1000)
        self.basic = basic
        self.tracer = {}

    def collect_word_list(
            self,
            basic=None,
            verbose=True,
            collect_tips_only=True):
        columns = ('doculect', 'concept', 'ipa', 'cogid')
        word_list = pandas.DataFrame(
            columns=columns,
            data=[['None', 0, 0, 0]])
        meaning_cogid_pairs = {}
        for i, node in enumerate(self.tree.preorder()):
            if node.Name == 'root':
                self.tracer[node.Name] = {
                        'language': self.root,
                        'distance': 0}
            else:
                new_language = self.tracer[
                    node.Parent.Name]['language'].clone()
                distance = random.randint(*self.change_range)
                if verbose:
                    print('... analyzing node {0} ({1})'.format(
                        node.Name, distance))

                for _ in range(distance):
                    new_language.change(self.related_concepts)
                self.tracer[node.Name] = {
                        'language': new_language,
                        'distance': distance}
                if not collect_tips_only or node.istip():
                    for concept, word in new_language.basic_vocabulary(
                            self.basic):
                        x = (0
                             if word_list['doculect'][0] == 'None'
                             else len(word_list))
                        word_list.loc[x] = (
                            node.Name, concept, word,
                            meaning_cogid_pairs.setdefault(
                                (concept, word),
                                len(meaning_cogid_pairs)))
        return word_list
