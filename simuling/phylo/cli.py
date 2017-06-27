#!/usr/bin/env python

"""Core functions for the command line interface."""


def basic_vocabulary_sampler(strings):
    """Factory for creating vocabulary samplers.

    For concept entries given by integer ID or name, create a basic
    vocabulary sampler function sampling these concepts.

    """
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
