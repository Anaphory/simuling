import random
from .language import Language


class Phylogeny(object):
    """A phylogenetic linguistic simulation"""

    def __init__(
            self,
            related_concepts,
            tree,
            root=None,
            basic=range(100),
            change_range=(500, 1000),
            initial_max_wt=10):
        self.related_concepts = related_concepts
        self.tree = tree

        if root is None:
            self.root = Language(
                self.related_concepts, initial_max_wt)
        else:
            self.root = root
        self.change_range = change_range
        self.basic = basic
        self.tracer = {}

    def simulate(self,
                 verbose=True):
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
                    new_language.change()
                self.tracer[node.Name] = {
                        'language': new_language,
                        'distance': distance}

    def collect_word_list(
            self,
            method=None,
            collect_tips_only=True):
        """Collect word lists from all (tip) languages in the tree.

        Create a CLDF-/lingpy-like list of (language_id, feature_id,
        value, cognate_class) tuples by sampling each language
        according to method.

        Parameters:

        `method`: A function Language → sequence of (concept, word)
          pairs, such as `Language.basic_vocabulary`, which is the
          default.

        `collect_tips_only`: boolean
          If True, collect word lists from the tips only, otherwise
          from every node in the tree. Default: True.
        """
        if method is None:
            def method(language):
                return Language.basic_vocabulary(language, self.basic)

        columns = ('doculect', 'concept', 'ipa', 'cogid')
        word_list = []
        concept_cogid_pairs = {}

        for i, node in enumerate(self.tree.preorder()):
            if not collect_tips_only or node.istip():
                language = self.tracer[node.Name]['language']
                for concept, word in method(language):
                    word_list.append((
                        node.Name,
                        concept,
                        word,
                        concept_cogid_pairs.setdefault(
                            (concept, word),
                            len(concept_cogid_pairs))))
        return word_list, columns
