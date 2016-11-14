from collections import defaultdict
from itertools import combinations
import lingpy
import random

from .bipartite import MultiBipartite


class Language(object):
    """
    A language is modelled as a bipartite graph.

    Notes
    -----
    Nothing special, we have words, concepts, and relations between the
    concepts (concepts belong to clusters of semantic fields). All very simple
    and rather tweaky.

    Parameter
    ---------
    signs: the number of concepts and words.
        We initialize by having the same number of signs and words, and then
        cross-link them, allowing for n-n links.
    fields: the number of semantic fields
        Fields are randomly assigned.
    max_syns: maximal number of synonyms
        This restricts the number of links between meanings and words upon
        initialization.
    params: parameters for random selection
        Dunno if this is the right approach, but so far, we have:
        * ll: lose link parameter
        * al: add link parameter
        * nw: new word parameter
        * ww: parameter to handle the probability of cross-linking concept and
              word connections upon initialization
    """
    def __init__(self,
                 signs, fields, max_syns=2, params=None):

        self.params = params or dict(
                ll=2,
                al=2,
                nw=10,
                ww=10,
                )
        self.concepts = list(range(signs))
        self.words = list(range(signs))
        self.fields = list(range(fields))

        # distribute fields over concepts
        self.concept2field = {}
        for c in self.concepts:
            self.concept2field[c] = random.choice(self.fields)

        self._signs = MultiBipartite({})
        self.concept2form = defaultdict(set)
        for i, j in combinations(self.concepts, r=2):
            if not random.randint(0, 1):
                if len(self.concept2form[i]) >= max_syns:
                    pass
                else:
                    for k in range(random.randint(0, self.params['ww'])):
                        self._signs.add(i, j)
                    self.concept2form[i].add(j)

        self.tracer = [self._signs]

    def _lose_link(self):
        """
        Delete a link from the set of links.

        Note
        ----
        Weights are modelled as recurring links in the list. This makes it
        easier (at least for me ...) to handle the selection process in a
        stochastic (?) manner (links which occur frequently are more likely to
        be deleted).
        """

        idx = random.randint(0, len(self._signs)-1)
        for key, values in self._signs.forwards.items():
            for value, frequency in values.items():
                idx -= frequency
                if idx <= 0:
                    self._signs.remove(key, value)
                    return
        raise ValueError("idx was too large")
    
    def remove_links(self, number):
        for i in range(number):
            idx = random.randint(0, len(self._signs)-1)
            for key, values in self._signs.forwards.items():
               for value, frequency in values.items():
                   idx -= frequency
                   if idx <= 0:
                       self._signs.remove(key, value)
                       return

    def add_links(self, number):
        
        widxs = [random.choice(self.words) for i in range(number)]
        targets = defaultdict(list)
        for c in self.concepts:
            targets[self.concept2field[c]] += [c]
        for widx in widxs:
            try:
                concepts = self._signs.inv[widx]
            except KeyError:
                concepts = []
            fields = [self.concept2field[c] for c in concepts]
            if fields:
                _targets = []
                for f in fields:
                    _targets += targets[f]
                new_link = random.choice(_targets)
                self._signs.add(new_link, widx)

    def _add_link(self):
        """
        Add a link between a concept and a word.

        Note
        ----
        Starts from choosing a 'word', then searches for the semantic fields in
        which that words occurs (maybe more, we are open for transitions, due
        to, e.g., homophony), and then select the new 'concept' from this
        restricted set.
        """
        
        widx = random.choice(self.words)

        # get the concepts
        try:
            concepts = self._signs.inv[widx]
        except KeyError:
            return

        # get the semantic fields
        fields = [self.concept2field[c] for c in concepts]

        if fields:
            targets = [c
                       for c in self.concepts
                       if self.concept2field[c] in fields]

            new_link = random.choice(targets)
            self._signs.add(new_link, widx)

    def _add_word(self, words=[]):
        """
        Add another word to the language.

        Note
        ----
        'words' is a list showing words that have been newly created in other
        languages so far, to avoid that this language creates the same ones.
        """

        if words:
            new_word = max(words)+1
        else:
            new_word = max(self.words)+1
        concept = random.choice(self.concepts)
        self._signs.add(concept, new_word)
        self.words += [new_word]

    def add_words(self, number, words=[]):
        if words:
            new_word = max(words) + 1
        else:
            new_word = max(self.words)+1
        for i in range(number):
            concept = random.choice(self.concepts)
            self._signs.add(concept, new_word)
            self.words += [new_word]
            new_word += 1

    def clone(self):
        """
        Make a copy of a language of itself. Needed for phylogenies.
        """

        tmp = Language(1, 1)
        tmp.concepts = [i for i in self.concepts]
        tmp.words = [i for i in self.words]
        tmp.fields = [i for i in self.fields]
        tmp.concept2field = dict([(a, b) for a, b in
                                  self.concept2field.items()])
        tmp._signs = MultiBipartite(
            self._signs.forwards.copy())
        tmp.tracer = [tmp._signs]
        return tmp

    def change(self, time, ctype=1, words=[]):
        """
        Basic process time is an integer.

        Notes
        -----
        'words' are needed to make sure the language creates NEW words, not the
        ones that have been created by another language.
        """

        if ctype == 1:
            for i in range(time):
                if random.randint(0, self.params['ll']):
                    self._lose_link()
                if random.randint(0, self.params['al']):
                    self._add_link()
                if not random.randint(0, self.params['nw']):
                    self._add_word(words)
        else:
            addlinks = 0
            remlinks = 0
            newwords = 0
            for i in range(time):
                if random.randint(0, self.params['ll']):
                    self._lose_link()
                    #remlinks += 1
                if random.randint(0, self.params['al']):
                    addlinks += 1
                if not random.randint(0, self.params['nw']):
                    newwords += 1
            self.remove_links(remlinks)
            self.add_links(addlinks)
            self.add_words(newwords)

        self.tracer.append(self._signs)

    def count(self, basic):
        basics = {}
        for idx in basic:
            refs = self._signs.forwards
            refs_sorted = sorted(refs,
                                 key=lambda x: len(refs[x]),
                                 reverse=True)
            if refs:
                best_refs = sum([len(refs[x]) for x in refs_sorted[:3]])
                selected = [
                    x
                    for x in refs_sorted[:3]
                    if len(refs[x]) > best_refs / 3] or [refs_sorted[0]]
            else:
                selected = []
            basics[idx] = selected
        return basics


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

        self.language = Language(
            signs, fields, max_syns=max_syns, params=params)
        params = params or self.language.params
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
        self.words = self.language.words
        self.log = dict(
                root=self.language.tracer[0]
                )
        self.tracer = {}
        self.siblings = {}
        for node in self.tree.preorder():
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

                new_language.change(distance, words=self.words, ctype=0)
                self.tracer[node.Name] = dict(
                        language=new_language,
                        tracer=new_language.tracer[1],
                        distance=distance)
                self.words += [w
                               for w in new_language.words
                               if w not in self.words]
                if node.istip():
                    self.siblings[node.Name] = new_language.count(self.basic)

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
