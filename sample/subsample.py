#!/usr/bin/env python

"""Samples a wordlist.

Provide functions and a cli interface to sample Swadesh-style word
lists with cognate coding and cognate class presence/absence tables
from input whole-vocabulary word lists.

"""

import collections
import sys
import argparse
import csv


from pyconcepticon.api import Concepticon


def swadesh_sampler(vocabulary, n_items=200, max_synonyms=1,
                    cross_semantic_cognates=False, **kwargs):
    """Build a Swadesh-like word list from a vocabulary.

    Extract the within-concept cognate classes representing the most
    dominant `max_synonyms` words for the most prevalent `n_items`
    concepts.

    """
    basic_concepts = collections.Counter()
    words_for_concept = {}
    languages = set()
    if not cross_semantic_cognates:
        set_mapper = {}
    for i, line in enumerate(vocabulary):
        concept = line["Feature_ID"]
        language = line["Language_ID"]
        weight = float(line["Weight"])
        concept_set = line["Concept_CogID"]

        if not cross_semantic_cognates:
            concept_set = set_mapper.setdefault(
                (concept, concept_set),
                len(set_mapper))

        languages.add(language)
        basic_concepts[concept] += weight
        synonyms = words_for_concept.setdefault(
            concept, {}).setdefault(language, collections.Counter())
        synonyms[concept_set] += weight

    # Output
    yield ("Language_ID", "Feature_ID", "Value")
    for concept, sum_weight in basic_concepts.most_common(n_items):
        for language in languages:
            items = words_for_concept[concept].get(language)
            if not items:
                yield (language, concept, "-")
            else:
                for cognate_set, weight in items.most_common(max_synonyms):
                    yield (language, concept, cognate_set)


def conceptlist_sampler_factory(conceptlist, name):
    """Create a Swadesh-like sampler for a given concept list."""
    def conceptlist_sampler(vocabulary, cross_semantic_cognates=False,
                            max_synonyms=1, **kwargs):
        """Build a word list from a vocabulary.

        Extract the within-concept cognate classes representing the
        most dominant `max_synonyms` words for the concepts of the
        list {:s}.

        """
        words_for_concept = {concept.concepticon_gloss: {}
                             for concept in conceptlist.concepts.values()}

        if not cross_semantic_cognates:
            set_mapper = {}
        for i, line in enumerate(vocabulary):
            concept = line["Feature_ID"].upper()
            if concept not in words_for_concept:
                continue

            language = line["Language_ID"]
            weight = float(line["Weight"])
            concept_set = line["Concept_CogID"]

            if not cross_semantic_cognates:
                concept_set = set_mapper.setdefault(
                    (concept, concept_set),
                    len(set_mapper))

            synonyms = words_for_concept[concept].setdefault(
                language, collections.Counter())
            synonyms[concept_set] += weight

        # Output
        yield ("Language_ID", "Feature_ID", "Value")
        for concept, words in words_for_concept.items():
            for language, items in words.items():
                for cognate_set, weight in items.most_common(max_synonyms):
                    yield (language, concept, cognate_set)
    conceptlist_sampler.__doc__ = conceptlist_sampler.__doc__.format(
        name)
    return conceptlist_sampler


def cognate_presence_sampler(vocabulary, min_activation=1, **kwargs):
    """List the presence/absence of all cognate classes in the vocabulary.

    Generate a CLDF-like list that notes for every language and
    cognate class whether that cognate class is present
    (i.e. Weight>min_activation) or absent in the language.
    """
    languages = set()
    cognate_classes = set()
    present = set()
    for i, line in enumerate(vocabulary):
        language = line["Language_ID"]
        weight = float(line["Weight"])
        cognate_class = line["Global_CogID"]
        if weight > min_activation:
            languages.add(language)
            cognate_classes.add(cognate_class)
            present.add((language, cognate_class))
    # Output
    yield ("Language_ID", "Feature_ID", "Value")
    for language in languages:
        for cognate_class in cognate_classes:
            yield (language,
                   cognate_class,
                   (language, cognate_class) in present)


samplers = {
    'swadesh': swadesh_sampler,
    'etymo': cognate_presence_sampler
}
cn = Concepticon()
for name, conceptlist in cn.conceptlists.items():
    samplers[name] = conceptlist_sampler_factory(conceptlist, name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Swadesh-sample a whole-vocabulary word list")
    parser.add_argument("--vocabulary-file", type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="CLDF word list of the complete lexicon")
    parser.add_argument("--output", "-o", type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument("--fasta", "-f", action="store_true", default=False,
                        help="Output in FASTA format, instead of CLDF")
    parser.add_argument("--sampler", "-s", default="swadesh",
                        choices=list(samplers.keys()),
                        help="The sampling method to use")
    group = parser.add_argument_group("Swadesh-style word lists")
    group.add_argument(
        "--swadesh", action="store_const", const="swadesh",
        dest="sampler",
        help="""Sample a Swadesh word list of cognate classes in meaning
        slots. Equivalent to --sampler=swadesh""")
    group.add_argument(
        "--cross-semantic-cognates",
        action='store_true',
        default=False,
        help="Keep cross-semantic cognate classes."
        " Do not split cognate classes to imply concepts.")
    group.add_argument(
        "--n-items", type=int, default=200,
        help="Number of items in the word list")
    group.add_argument(
        "--max-synonyms", type=int, default=1,
        help="Maximum number of synonyms for each word list entry")
    group = parser.add_argument_group(
        "Etymological dictionary-style word lists")
    group.add_argument(
        "--etymo", action="store_const", const="etymo",
        dest="sampler",
        help="""Sample an etymological dictionary, i.e. a CLDF that lists for every
        known root whether or not that root has a reflex in the
        language.""")
    group.add_argument(
        "--min-activation", type=float, default=1,
        help="""The minimum weight value of words in the vocabulary to be included
in the etymological dictionary.""")
    args = parser.parse_args()

    data = csv.DictReader(args.vocabulary_file, dialect='excel-tab')
    sampler = samplers[args.sampler](data, **vars(args))
    if args.fasta:
        ...
        raise NotImplementedError("FASTA output is not available")
    else:
        writer = csv.writer(args.output)
        sampler = samplers[args.sampler]
        writer.writerows(sampler(data, **vars(args)))
