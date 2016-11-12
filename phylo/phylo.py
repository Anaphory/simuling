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
            initial_max_wt=10):
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
        word_list = []
        concept_cogid_pairs = {}
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
                if not collect_tips_only or node.istip():
                    for concept, word in new_language.basic_vocabulary(
                            self.basic):
                        word_list.append((
                            node.Name,
                            concept,
                            word,
                            concept_cogid_pairs.setdefault(
                                (concept, word),
                                len(concept_cogid_pairs))))
        return word_list, columns
