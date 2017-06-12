"""Framework for a phylogenetic semantic/lexical change simulation.

Phylogeny – the core simulation class.

"""

from .naminggame import NamingGameLanguage as Language


class Phylogeny(object):
    """A phylogenetic linguistic simulation.

    Create a simulation object on a given rooted tree with branch
    lengths.

    """

    def __init__(
            self,
            related_concepts,
            tree,
            initial_weight,
            root=None,
            basic=range(100),
            scale=1000,
            neighbor_factor=0.1):
        """Create a phylogeny simulation object.

        related_concepts: a networkx.Graph or a dictionary of lists,
        describing which concepts can evolve into which other concepts.

        tree: The phylogenetic tree along which to run the simulation.

        root: The phylo.Language to use at the root.

        """
        self.related_concepts = related_concepts
        self.tree = tree

        if root is None:
            self.root = Language(
                self.related_concepts,
                neighbor_factor=neighbor_factor)
            self.root.generate_words(initial_weight)
        else:
            self.root = root
        self.scale = scale
        self.basic = basic
        self.tracer = {}

    def simulate(self,
                 verbose=1,
                 **simargs):
        """Run a simulation down the tree.

        Evolve languages down the branches of the tree, changing
        proportional to the branch lengths.

        """
        for i, node in enumerate(self.tree.walk('preorder')):
            if node.ancestor is None:
                self.tracer[node] = {
                    'language': self.root,
                    'distance': 0}
                if verbose >= 1:
                    print('... initializing node {0} (root)'.format(
                        node.name))
            else:
                new_language = self.tracer[
                    node.ancestor]['language'].clone()
                distance = int(
                    (node.length or 1) * self.scale)
                if verbose >= 1:
                    print('... analyzing node {0} ({1})'.format(
                        node.name, distance))

                for _ in range(distance):
                    new_language.change(**simargs)
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
