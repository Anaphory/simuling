#!/usr/bin/env python

"""Language model.

This module supplies the functionality of a basic language model.

"""

import pandas
import numpy
import bisect

class Language(object):
    """A simulated language.

    The language is at its core a mutable m-to-n Saussurean mapping
    between concepts and words (which are represented by
    `int`s). Words can change their meaning, and new words can arise
    over time.

    """

    max_word = 0
    """The first unused word index.

    This integer will be used and increased when a language invents a
    new word.

    """

    random = numpy.random
    """Random number generator to use."""

    def __init__(self,
                 related_concepts,
                 initial_max_wt=10,
                 random=numpy.random):
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

        self.random = random

        # The weighted word-concept map is represented by a
        # `pandas.Series` containing the *cumulative* weights, because
        # that makes our most frequent calculation, the weighted
        # random choice, very fast, and in the average case should net
        # us about half a complete iteration of the list advantage of
        # calculating it anew every draw step.
        
        # It is not easy to create an empy MultiIndex, so we create a
        # non-empty one and delete the entry.
        self._cum_concept_weights = pandas.Series(
            index=pandas.MultiIndex.from_tuples(
                [(-1, -1)],
                names=["concept", "word"]))
        del self._cum_concept_weights[(-1, -1)]
        cum_weight = 0

        n_words = len(related_concepts)
        for i in range(Language.max_word,
                       Language.max_word+n_words):
            # Draw a random weight according to `initial_max_wt`. (And
            # immediately add it to the cumulative weight.)
            cum_weight += self.random.randint(initial_max_wt)+1
            self._cum_concept_weights[
                self.random.randint(len(related_concepts)),
                i] = cum_weight

        # None of the words in this language should be cognate with
        # words in other languages, so we need to adjust the minimum
        # new word pointer.
        Language.max_word += n_words

    def random_edge(self):
        draw = self._cum_concept_weights
        max = draw.iloc[-1]
        point = self.random.random() * max
        return draw.index[bisect.bisect(draw.values, point)]

    def words_for_concept(self, concept):
        index = self._cum_concept_weights.index
        return index.get_level_values(
            'word').values[
                index.get_level_values('concept').values == concept]

    def concepts_for_word(self, word):
        index = self._cum_concept_weights.index
        return self._cum_concept_weights.index.get_level_values(
            'concept').values[
                index.get_level_values('word').values == word]

    def loss(self):
        concept, word = self.random_edge()
        i = self._cum_concept_weights.index.get_loc((concept, word))
        self._cum_concept_weights.values[i:] -= 1
        new_val = self._cum_concept_weights.iloc[i]
        if (new_val == 0 or
                new_val == self._cum_concept_weights.iloc[i-1]):
            del self._cum_concept_weights[concept, word]

    def gain(self, related_concepts):
        concept, word = self.random_edge()
        rc = related_concepts[concept]
        new_concept = list(rc)[self.random.randint(len(rc))]
        try:
            i = self._cum_concept_weights.index.get_loc((concept, word))
            self._cum_concept_weights.values[i:] += 1
        except KeyError:
            self._cum_concept_weights[
                new_concept,
                word] = self._cum_concept_weights.iloc[-1] + 1

    def new_word(self, rc):
        new_concept = list(rc)[self.random.randint(len(rc))]
        self._cum_concept_weights[
            new_concept,
            Language.max_word] = (
                self._cum_concept_weights.iloc[-1] + 1)
        Language.max_word += 1

    def flat_frequencies(self):
        v = self._cum_concept_weights.values
        return pandas.Series(
            index=self._cum_concept_weights.index,
            data=numpy.concatenate(
                ([v[0]], v[1:]-v[:-1])))

    def basic_vocabulary(self, basic, threshold=3):
        weights = self.flat_frequencies()
        for concept in basic:
            words_for = weights[
                self._cum_concept_weights.index.get_level_values(
                    'concept').values == concept]
            best_words = words_for.sort_values()[-threshold:]
            target_weight = best_words.sum()/threshold
            for index, weight in best_words.items():
                if weight>target_weight:
                    yield index

    def change(self, related_concepts,
               p_lose=0.5,
               p_gain=0.4,
               p_new=0.1):
        if self.random.random() < p_lose:
            self.loss()
        if self.random.random() < p_gain:
            self.gain(related_concepts)
        if self.random.random() < p_new:
            self.new_word(related_concepts)

    def clone(self):
        l = Language({})
        l._cum_concept_weights = self._cum_concept_weights.copy()
        return l

    def __repr__(self):
        return "<Language\n{:}>".format(
            self.flat_frequencies())
