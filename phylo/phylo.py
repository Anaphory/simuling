from .naminggame import NamingGameLanguage as Language


class Phylogeny(object):
    """A phylogenetic linguistic simulation"""

    def __init__(
            self,
            related_concepts,
            tree,
            root=None,
            basic=range(100),
            scale=1000,
            initial_max_wt=10):
        self.related_concepts = related_concepts
        self.tree = tree

        if root is None:
            self.root = Language(
                self.related_concepts, initial_max_wt)
        else:
            self.root = root
        self.scale = scale
        self.basic = basic
        self.tracer = {}

    def simulate(self,
                 verbose=True,
                 p_lose=0.5,
                 p_gain=0.4,
                 p_new=0.1):
        for i, node in enumerate(self.tree.walk('preorder')):
            if node.ancestor is None:
                self.tracer[node] = {
                    'language': self.root,
                    'distance': 0}
                print('... initializing node {0} (root)'.format(
                    node.name))
            else:
                new_language = self.tracer[
                    node.ancestor]['language'].clone()
                distance = int(
                    (node.length or 1) * self.scale)
                if verbose:
                    print('... analyzing node {0} ({1})'.format(
                        node.name, distance))

                for _ in range(distance):
                    new_language.change(p_lose, p_gain, p_new)
                self.tracer[node] = {
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

        columns = ("ID", "Language_ID", "Feature_ID", "Value",
                   "Weight", "Global_CogID", "Concept_CogID")
        word_list = []
        concept_cogid_pairs = {}

        i = 0
        for _, node in enumerate(self.tree.walk('preorder')):
            if not collect_tips_only or node.is_leaf:
                language = self.tracer[node]['language']
                for concept, word, weight in method(language):
                    i += 1
                    word_list.append((
                        i,
                        node.name,
                        concept,
                        "",  # This would be the IPA string or
                             # something like that.
                        weight,
                        word,
                        concept_cogid_pairs.setdefault(
                            (concept, word),
                            len(concept_cogid_pairs) + 1)))
        return word_list, columns
