import random
import collections
from pathlib import Path

from csvw import UnicodeDictReader, UnicodeWriter

from .cli import argparser, phylogeny
from .simulation import (SemanticNetwork, parse_distribution_description,
                         Language, simulate, echo)

args = argparser().parse_args()
phylogeny = phylogeny(args)

random.seed(args.seed)

if args.semantic_network:
    semantics = SemanticNetwork.load_from_gml(
        args.semantic_network, args.weight_attribute)
else:
    semantics = SemanticNetwork.load_from_gml(
        (Path(__file__).absolute().parent.parent /
            "phylo" / "network-3-families.gml").open(),
        args.weight_attribute)
semantics.neighbor_factor = args.neighbor_factor

weight = parse_distribution_description(args.weight)
if args.wordlist:
    languages = collections.OrderedDict()
    reader = UnicodeDictReader(args.wordlist)
    for line in reader:
        language_id = line["Language_ID"]
        if args.language and language_id != args.language:
            continue
        concept = line["Parameter_ID"]
        try:
            wt = int(line["Weight"])
        except KeyError:
            wt = weight()
        word_weights = languages.setdefault(
            language_id, {}).setdefault(
                concept, collections.defaultdict(
                    lambda: 0, {}))
        word_weights[line["Cognateset_ID"]] = wt
    if args.language is None:
        args.language = list(languages)[-1]
    language = Language(languages[args.language],
                        semantics)
else:
    raw_language = {
        concept: collections.defaultdict(
            (lambda: 0), {c: weight()})
        for c, concept in enumerate(semantics)}
    language = Language(raw_language, semantics)
    Language.max_word = len(raw_language)
with UnicodeWriter(args.output_file, commentPrefix="# ") as writer:
    writer.writerow(
        ["Language_ID", "Parameter_ID", "Cognateset_ID", "Weight"])
    if args.embed_parameters:
        for arg, value in echo(args):
            writer.writecomment(
                "--{:s} {:}".format(
                    arg, value))
    for id, data in simulate(phylogeny, language):
        with Path("test.log").open("a") as log:
            for concept, words in data.items():
                for word, weight in words.items():
                    if weight:
                        writer.writerow([
                            id,
                            concept,
                            word,
                            weight])
