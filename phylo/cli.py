#!/usr/bin/env python


def basic_vocabulary_sampler(strings):
    concepts = []
    for entry in strings:
        try:
            concepts.append(int(entry))
        except ValueError:
            concepts.append(entry)
    if type(strings) == range:
        name = "b{:d}".format(len(strings))
    else:
        name = "b{:}{:d}".format(concepts[0], len(concepts))
    return (name,
            lambda language: language.basic_vocabulary(concepts))
