import sys
import argparse

import collections
import numpy.random
from pathlib import Path

from csvw import UnicodeDictReader

from .cli import (
    argparser, phylogeny, echo, parse_distribution_description,
    concept_weights, default_network)
from .simulation import (SemanticNetworkWithConceptWeight, Language,
                         Multiprocess, simulate, constant_zero)
from .io import CommentedUnicodeWriter


def concept_weight(concept):
    return concept_weights[args.concept_weight](len(semantics[concept]))

parser = argparser()
args = parser.parse_args()

if args.multiprocess != 1:
    simulate = Multiprocess(args.multiprocess).simulate
if args.resume:
    resume = True
    simulate = Multiprocess(args.multiprocess).simulate_remainder
else:
    resume = False

weight = parse_distribution_description(
    args.weight,
    random=numpy.random.RandomState(args.seed))

phylogeny = phylogeny(args)


if args.semantic_network:
    semantics = SemanticNetworkWithConceptWeight.load_from_gml(
        args.semantic_network, args.weight_attribute)
else:
    semantics = SemanticNetworkWithConceptWeight.load_from_gml(
        default_network.open(),
        args.weight_attribute)
semantics.neighbor_factor = args.neighbor_factor

semantics.concept_weight = concept_weight

if args.wordlist:
    languages = collections.OrderedDict()
    with UnicodeDictReader(args.wordlist) as reader:
        for line in reader:
            language_id = line["Language_ID"]
            if not resume and args.language and language_id != args.language:
                continue
            concept = line["Parameter_ID"]
            try:
                wt = int(line["Weight"])
            except KeyError:
                wt = weight()
            word_weights = languages.setdefault(
                language_id, {}).setdefault(
                    concept, collections.defaultdict(
                        constant_zero, {}))
            word_weights[line["Cognateset_ID"]] = wt
    if resume:
        simulator = Multiprocess(args.multiprocess)
        for name, lang in languages.items():
            simulator.generated_languages[name] = Language(lang, semantics)
        simulate = simulator.simulate_remainder
        # Resuming when the root language is not available doesn't make any
        # sense, so fill the root language with a nonsense value that will
        # raise an error later. FIXME: Make the later error message more
        # transparent.
        language = None
    else:
        if args.language is None:
            args.language = list(languages)[-1]
        language = Language(languages[args.language],
                            semantics)
else:
    raw_language = {
        concept: collections.defaultdict(
            constant_zero, {c: weight()})
        for c, concept in enumerate(semantics)}
    language = Language(raw_language, semantics)
    Language.max_word = len(raw_language)

with CommentedUnicodeWriter(args.output_file, commentPrefix="# ") as writer:
    writer.writerow(
        ["Language_ID", "Parameter_ID", "Cognateset_ID", "Weight"])
    if args.embed_parameters:
        for arg, value in echo(args):
            writer.writecomment(
                "--{:s} {:}".format(
                    arg, value))
    for id, data in simulate(phylogeny, language,
                             seed=args.seed,
                             writer=writer):
        print("Language {:} generated.".format(id))
