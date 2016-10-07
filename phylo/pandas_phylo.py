import pandas
import numpy
import bisect


class Language:
    def __init__(self, related_concepts, initial_max_wt=10):
        n_words = len(related_concepts)
        self.concept_weights = pandas.Series(
            index=pandas.MultiIndex.from_tuples(
                [(0, 0)],
                names=["concept", "word"]))
        del self.concept_weights[(0, 0)]
        cum_weight = 0
        for i in range(1, n_words):
            cum_weight += numpy.random.randint(initial_max_wt)+1
            self.concept_weights[
                numpy.random.randint(len(related_concepts)),
                i] = cum_weight
        print(self.concept_weights)

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
        new_concept = rc[numpy.random.randint(len(rc))]
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
            self.concept_weights.index.levels[1].max()+1] = (
                self.concept_weights.iloc[-1] + 1)


rc = {i: range(10) if i < 10 else range(10, 20)
      for i in range(20)}
l = Language(rc)
for c in range(20):
    l.loss()
    l.loss()
    l.loss()
    l.loss()
    l.gain(rc)
    l.gain(rc)
    l.gain(rc)
    l.new_word(rc)
    print(l.concept_weights)
