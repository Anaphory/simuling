import pandas
import numpy
import bisect


class Language:
    max_word = 0

    def __init__(self, related_concepts, initial_max_wt=10):
        n_words = len(related_concepts)
        self.concept_weights = pandas.Series(
            index=pandas.MultiIndex.from_tuples(
                [(-1, -1)],
                names=["concept", "word"]))
        del self.concept_weights[(-1, -1)]
        cum_weight = 0
        for i in range(Language.max_word,
                       Language.max_word+n_words):
            cum_weight += numpy.random.randint(initial_max_wt)+1
            self.concept_weights[
                numpy.random.randint(len(related_concepts)),
                i] = cum_weight
        Language.max_word += n_words

    def random_edge(self):
        draw = self.concept_weights
        max = draw.iloc[-1]
        point = numpy.random.random() * max
        return draw.index[bisect.bisect(draw.values, point)]

    def words_for_concept(self, concept):
        index = self.concept_weights.index
        return index.get_level_values(
            'word').values[
                index.get_level_values('concept').values == concept]

    def concepts_for_word(self, word):
        index = self.concept_weights.index
        return self.concept_weights.index.get_level_values(
            'concept').values[
                index.get_level_values('word').values == word]

    def loss(self):
        concept, word = self.random_edge()
        i = self.concept_weights.index.get_loc((concept, word))
        self.concept_weights.values[i:] -= 1
        new_val = self.concept_weights.iloc[i]
        if (new_val == 0 or
                new_val == self.concept_weights.iloc[i-1]):
            del self.concept_weights[concept, word]

    def gain(self, related_concepts):
        concept, word = self.random_edge()
        rc = related_concepts[concept]
        new_concept = list(rc)[numpy.random.randint(len(rc))]
        try:
            i = self.concept_weights.index.get_loc((concept, word))
            self.concept_weights.values[i:] += 1
        except KeyError:
            self.concept_weights[
                new_concept,
                word] = self.concept_weights.iloc[-1] + 1

    def new_word(self, rc):
        new_concept = list(rc)[numpy.random.randint(len(rc))]
        self.concept_weights[
            new_concept,
            Language.max_word] = (
                self.concept_weights.iloc[-1] + 1)
        Language.max_word += 1

    def flat_frequencies(self):
        v = self.concept_weights.values
        return pandas.Series(
            index=self.concept_weights.index,
            data=numpy.concatenate(
                ([v[0]], v[1:]-v[:-1])))

    def basic_vocabulary(self, basic, threshold=3):
        weights = self.flat_frequencies()
        for concept in basic:
            words_for = weights[
                self.concept_weights.index.get_level_values(
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
        if numpy.random.random() < p_lose:
            self.loss()
        if numpy.random.random() < p_gain:
            self.gain(related_concepts)
        if numpy.random.random() < p_new:
            self.new_word(related_concepts)

    def clone(self):
        l = Language({})
        l.concept_weights = self.concept_weights.copy()
        return l
