#!/usr/bin/env python


"""Language model.

This module supplies the functionality of a basic language model.

"""


import random
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

    rng = random.Random()
    """Random number generator to use."""

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

        self._cum_concept_weights = []
        self._word_meaning_pairs = []
        cum_weight = 0

        n_words = len(related_concepts)
        for i in range(Language.max_word,
                       Language.max_word + n_words):
            # Draw a random weight according to `initial_max_wt`. (And
            # immediately add it to the cumulative weight.)
            cum_weight += self.rng.randrange(initial_max_wt) + 1
            self._cum_concept_weights.append(cum_weight)
            self._word_meaning_pairs.append((
                i,
                self.rng.choice([x for x in related_concepts])))

        assert len(self._cum_concept_weights) == len(self._word_meaning_pairs)
        # None of the words in this language should be cognate with
        # words in other languages, so we need to adjust the minimum
        # new word pointer.
        Language.max_word += n_words

        self._flat = None

    def random_edge(self, return_word_meaning_pair=True):
        draw = self._cum_concept_weights
        max = draw[-1]
        point = self.rng.random() * max
        index = bisect.bisect(draw, point)
        if return_word_meaning_pair:
            return self._word_meaning_pairs[index]
        else:
            return index

    def words_for_concept(self, concept):
        return {word
                for word, meaning in self._word_meaning_pairs
                if meaning == concept}

    def concepts_for_word(self, word):
        return {meaning
                for word_, meaning in self._word_meaning_pairs
                if word_ == word}

    def clean(self, i):
        """Remove zero weights.

        Check whether the weight at index i is zero, and if so, remove
        that entry.

        """
        new_val = self._cum_concept_weights[i]
        if (new_val == 0 or
                new_val == self._cum_concept_weights[i - 1]):
            del self._cum_concept_weights[i]
            del self._word_meaning_pairs[i]

    def loss(self, proportional=True):
        """Remove weight from a word-meaning pair.

        If proportional is True, remove weight 1 from a word-meaning
        pair with probability proportional to the weight before the
        loss step. Otherwise, remove weight 1 from a uniform random
        word-meaning pair.

        """
        self._flat = None
        if proportional:
            i = self.random_edge(return_word_meaning_pair=False)
        else:
            i = self.rng.randrange(len(self._word_meaning_pairs))
        word, concept = self._word_meaning_pairs[i]
        for j in range(i, len(self._cum_concept_weights)):
            self._cum_concept_weights[j] -= 1
        self.clean(i)

    def gain(self, reduce_other=False):
        self._flat = None
        """Add a meaning to a word

        A random word (with probability proportional to ‘use’) gains
        the meaning of one concept related to a meaning it already
        has. If reduce_other is true, a random other word expressing
        that meaning loses weight 1.

        """
        word, concept = self.random_edge()
        rc = self.related_concepts[concept]
        new_concept = list(rc)[self.rng.randrange(len(rc))]
        other_index = len(self._cum_concept_weights)
        if reduce_other:
            other_words = self.words_for_concept(new_concept)
            other_words -= {word}
            if other_words:
                other_word = list(other_words)[
                    self.rng.randrange(len(other_words))]
                other_index = self._word_meaning_pairs.index(
                    (other_word, new_concept))
        try:
            new_index = self._word_meaning_pairs.index((word, new_concept))
            if new_index < other_index:
                for j in range(new_index, other_index):
                    self._cum_concept_weights[j] += 1
            else:
                for j in range(other_index, new_index):
                    self._cum_concept_weights[j] -= 1
        except ValueError:
            for j in range(other_index, len(self._cum_concept_weights)):
                self._cum_concept_weights[j] -= 1
            self._cum_concept_weights.append(
                self._cum_concept_weights[-1] + 1)
            self._word_meaning_pairs.append((
                word, new_concept))
        if reduce_other and other_index != len(
                self._cum_concept_weights):
            self.clean(other_index)

    def new_word(self):
        self._flat = None
        """A random concept gains an entirely new word"""
        rc = self.related_concepts
        new_concept = list(rc)[self.rng.randrange(len(rc))]
        self._cum_concept_weights.append(
            self._cum_concept_weights[-1] + 1)
        self._word_meaning_pairs.append(
            (Language.max_word,
             new_concept))
        Language.max_word += 1

    def flat_frequencies(self):
        if not self._flat:
            self._flat = {
                (word, meaning): (frequency - prev_frequency)
                for (word, meaning), frequency, prev_frequency in zip(
                    self._word_meaning_pairs,
                    self._cum_concept_weights,
                    [0] + self._cum_concept_weights)}
        return self._flat

    def basic_vocabulary(self, basic, threshold=3):
        weights = self.flat_frequencies()
        for concept in basic:
            best_words_for = []
            best_word_weights = []
            for (word, meaning), weight in weights.items():
                if meaning == concept:
                    if (
                            not best_word_weights) or (
                            weight > best_word_weights[0]):
                        i = bisect.bisect(
                            best_word_weights,
                            weight)
                        best_words_for.insert(i, word)
                        best_word_weights.insert(i, weight)

            weightsum = 0
            for i, (word, weight) in enumerate(zip(
                    reversed(best_words_for),
                    reversed(best_word_weights))):
                if i >= threshold:
                    break
                if weight < weightsum / (i + 0.5):
                    break
                yield (concept, word, weight)
                weightsum += weight

    def all_reflexes(self, threshold=0):
        """Sequence of all reflexes in the language

        For each cognate class (i.e. each word) that has any meaning
        with activation above `threshold`, give it and its most
        salient meaning.

        Language.all_reflexes is one possible value for the `method`
        argument of `Phylogeny.collect_wordlist`.

        """
        words = {}
        for (word, meaning), weight in self.flat_frequencies().items():
            old_meaning, old_weight = words.get(word, (None, threshold))
            if weight > old_weight:
                words[word] = (meaning, weight)
        for word, (meaning, weight) in words.items():
            yield (meaning, word, weight)

    def vocabulary(self):
        """Sequence of all forms/meaning-pairs in the language

        Language.vocabulary is one possible value for the `method`
        argument of `Phylogeny.collect_wordlist`.

        """
        for (word, meaning), weight in self.flat_frequencies().items():
            yield (meaning, word, weight)

    def change(self,
               p_lose=0.5,
               p_gain=0.4,
               p_new=0.1):
        if self.rng.random() < p_lose:
            self.loss()
        if self.rng.random() < p_gain:
            self.gain(reduce_other=True)
        if self.rng.random() < p_new:
            self.new_word()

    def clone(self):
        l = Language({})
        l._cum_concept_weights = self._cum_concept_weights[:]
        l._word_meaning_pairs = self._word_meaning_pairs[:]
        l.related_concepts = self.related_concepts
        return l

    def __repr__(self):
        return "<Language\n{:}>".format(
            self.flat_frequencies())
