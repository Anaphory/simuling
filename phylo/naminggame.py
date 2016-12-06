#!/usr/bin/env python


"""Language model based on a naming game

This module supplies the functionality of a language model that
evolves according to a process inspired by Naming Games.

"""


import random


from .language import Language
from collections import defaultdict, Counter


class NamingGameLanguage(Language):
    """A simulated language.

    The language is at its core a mutable m-to-n Saussurean mapping
    between concepts and words (which are represented by
    `int`s). Words can change their meaning, and new words can arise
    over time.

    """

    def __init__(self,
                 related_concepts,
                 initial_max_wt=10,
                 random=random.Random()):
        """Create a random language.

        Given a dictionary mapping concepts to their
        `related_concepts`, generate a new random language (i.e. a
        concept-word map) with on average one word for each concept.

        The connections in the word-concept map have weights, which
        will be initialized with a random integer between 1 and
        `initial_max_wt` inclusively.

        >>> Language({1:[2,3],2:[1],3:[2]})


        Args:
            related_concepts (`dict`): Maps concepts to semantically
                related concepts.

            initial_max_wt (`int`, optional): The maximum weight of a
                concept-word connection weight. Defaults to 10.

            random (`RandomState`, optional): The random number
                generator to use. Defaults to `numpy.random`.

        """

        self.rng = random

        # The weighted word-concept map is represented by two lists
        # containing the indices *cumulative* weights, because that
        # makes our most frequent calculation, the weighted random
        # choice, very fast, and in the average case should net us
        # about half a complete iteration of the list advantage of
        # calculating it anew every draw step.

        self.related_concepts = related_concepts

        self.words = defaultdict(Counter)
        n_words = len(related_concepts)
        for i in range(Language.max_word,
                       Language.max_word + n_words):
            weight = self.rng.randrange(initial_max_wt) + 1
            self.words[self.random_concept()][i] = weight

        Language.max_word += n_words

    def random_edge(self, return_word_meaning_pair=True):
        raise NotImplementedError

    def words_for_concept(self, concept):
        return set(self.words[concept])

    def concepts_for_word(self, word):
        return set(
            meaning for meaning, words in self.words.items()
            if word in words)

    def clean(self, i):
        raise NotImplementedError

    def gain(self, reduce_other=False):
        raise NotImplementedError

    def new_word(self):
        raise NotImplementedError

    def random_concept(self):
        rc = self.related_concepts
        return list(rc)[self.rng.randrange(len(rc))]

    def loss(self):
        """Remove weight 1 from a random word-meaning pair

        Select a random word-meaning pair with probability
        proportional to 1/weight (i.e. rare words more often) and
        reduce its weight by 1.

        """
        sum_reciprocal_weights = 0
        for meaning, words in self.words.items():
            for word, weight in words.items():
                sum_reciprocal_weights += 1/weight
        v = self.rng.random() * sum_reciprocal_weights
        for meaning, words in self.words.items():
            for word, weight in words.items():
                v -= weight
                if v < 0:
                    break
            else:
                continue
            break
        else:
            raise RuntimeError("Have the weights changed during iteration?")
        self.words[meaning][word] -= 1
        if self.words[meaning][word] <= 0:
            del self.words[meaning][word]
        if not self.words[meaning]:
            del self.words[meaning]

    def naming_game(self):
        word_sets = {}
        for _ in range(2):
            meaning = self.random_concept()
            while meaning in word_sets:
                # There are safer (no infinite loops, fewer randomizer
                # draws) ways to do this. They will require
                # appropriate methods and data structures though.
                meaning = self.random_concept()
            words = self.words[meaning].copy()
            for similar_meaning in self.related_concepts[meaning]:
                for word, weight in self.words[similar_meaning].items():
                    words.setdefault(word, 0)
                    words[word] += 0.5*weight
            word_sets[meaning] = words

        exclusively = {}
        non_specific_word = None
        non_specific_meaning = None
        non_specific_weight = 0
        for meaning, words in word_sets.items():
            for word, weight in words.items():
                if any(word in word_sets[other_meaning]
                       for other_meaning in word_sets
                       if other_meaning != meaning):
                    if self.words[meaning][word] > non_specific_weight:
                        non_specific_weight = self.words[meaning][word]
                        non_specific_word = word
                        non_specific_meaning = meaning
                else:
                    try:
                        if weight > exclusively[meaning][1]:
                            exclusively[meaning] = (word, weight)
                    except KeyError:
                        exclusively[meaning] = (word, weight)

        # There are four cases to distinguish: Are there exclusive
        # words, and are there non-exclusive words?
        for meaning in word_sets:
            if meaning in exclusively:
                word, weight = exclusively[meaning]
                self.words[meaning][word] += 1
            else:
                self.words[meaning][Language.max_word] = 1
                Language.max_word += 1

        if non_specific_word:
            self.words[non_specific_meaning][non_specific_word] -= 1
        else:
            self.loss()

    def flat_frequencies(self):
        return {
            (word, meaning): weight
            for meaning, words in self.words.items()
            for word, weight in self.words.items()}

    def change(self,
               p_lose=None,
               p_gain=None,
               p_new=None):
        self.loss()
        self.naming_game()

    def clone(self):
        l = NamingGameLanguage()
        # Probably use deepcopy instead
        l.words = {meaning:
                   {word: weight
                    for word, weight in words.items()}
                   for meaning, words in self.words.items()}
        l.related_concepts = self.related_concepts
        return l

    def __repr__(self):
        return "<NamingGameLanguage\n{:}>".format(
            self.flat_frequencies())
