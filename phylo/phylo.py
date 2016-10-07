from collections import defaultdict
from itertools import combinations
import lingpy
import random

from .bipartite import MultiBipartite


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

    def __init__(self, signs, fields, max_syns=2, params=None):
        # distribute fields over concepts
        self.related_concepts = {}
        concept2field = defaultdict(set)
        for c in range(signs):
            concept2field[random.randint(0, fields-1)].add(c)
        for field in concept2field.values():
            for concept in field:
                self.related_concepts[concept] = field - {concept}


        self.language = Language(self.related_concepts, max_syns)
        params = params or {}
        if 'change_range' not in params:
            params['change_range'] = 1000
        self.params = params

    def prepare(self, taxa, change_range=None, logfile='phylo.log',
                change_min=500):
        if change_range:
            self.params['change_range'] = change_range
        self.params['change_min'] = change_min
        self.tree = lingpy.basic.tree.Tree(lingpy.basic.tree.random_tree(
            taxa, branch_lengths=False))

    def start(self, basic=None, verbose=True):
        self.basic = basic or list(range(100))
        self.log = dict(
                root=self.language.tracer[0]
                )
        self.tracer = {}
        self.siblings = {}
        for i, node in enumerate(self.tree.preorder()):
            if node.Name == 'root':
                self.tracer[node.Name] = dict(
                        language=self.language,
                        tracer=self.language.tracer[0],
                        distance=0
                        )
            else:
                new_language = self.tracer[
                    node.Parent.Name]['language'].clone()
                distance = random.randint(
                    self.params['change_min'],
                    self.params['change_range'])
                if verbose:
                    print('... analyzing node {0} ({1})'.format(
                        node.Name, distance))

                for _ in range(distance):
                    new_language.change(self.related_concepts)
                self.tracer[node.Name] = dict(
                        language=new_language,
                        tracer=new_language.tracer[1],
                        distance=distance)
                if node.istip():
                    self.siblings[node.Name] = new_language.basic_vocabulary(self.basic)

    def wordlist(self):
        """
        Create a wordlist of the data (easy to use in lingpy).
        """

        D = {}
        idx = 1
        for concept in self.basic:
            for taxon in self.tree.taxa:
                for word in self.siblings[taxon][concept]:
                    D[idx] = [taxon, concept, 'word', word]
                    idx += 1
        D[0] = ['doculect', 'concept', 'ipa', 'cogid']
        wl = lingpy.basic.wordlist.Wordlist(D)
        return wl
