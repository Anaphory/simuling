"""Simulate lexical evolution based on gradual semantic shift.

"""

import collections
import numpy.random

import argparse
import tempfile
from clldutils.path import Path

from csvw import UnicodeDictReader
from csvw.dsv_dialects import Dialect
import newick

from .io import CommentedUnicodeWriter
from .simulation import (simulate, Multiprocess,
                         SemanticNetworkWithConceptWeight, constant_zero,
                         Language)

default_network = Path(__file__).absolute().parent / "network-3-families.gml"

concept_weights = {
    "one": lambda degree: 1,
    "degree": lambda degree: degree,
    "square": lambda degree: degree ** 2,
    "exponential": lambda degree: 2 ** degree}


def parse_distribution_description(text, random):
    try:
        name, parameters = text.strip().split("(")
    except ValueError:
        const = int(text.strip())
        return lambda: const
    if not parameters.endswith(")"):
        raise ValueError("Could not parse distribution string")
    function = {
        "uniform": lambda x: random.randint(1, x),
        "constant": lambda x: x,
        "geometric": lambda x: random.geometric(1 / x),
        "poisson": lambda x: random.poisson(x)}[name]
    args = [int(x) for x in parameters.split(",")]
    return lambda: function(args)


def argparser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    initialization = parser.add_argument_group(
        "Initializing the root language")
    initialization.add_argument(
        "--wordlist", type=argparse.FileType("r"),
        help="Load the root language from this CLDF Wordlist. (default: Create"
        " a new language with exactly one word for each concept.)")
    initialization.add_argument(
        "--language",
        help="Load this Language_ID from the CLDF Wordlist. (default: The one"
        " referred to in the last line of the table with the Cognateset_IDs.)")
    initialization.add_argument(
        "--weight",
        default="100",
        help="Random distribution to use when initializing the root language,"
        " if no weights are given in the CLDF Wordlist. (default: The"
        " distribution that always returns 100.)")
    parameters = parser.add_argument_group(
        "Simulation parameters")
    parameters.add_argument(
        "--semantic-network", type=argparse.FileType("r"),
        help="The semantic network, given as GML file. (default: CLICS.)")
    parameters.add_argument(
        "--neighbor-factor", type=float,
        default=0.004,
        help="The connection strength between adjacent concepts of edge weight"
        " 1 in the semantic network. (default: 0.004)")
    parameters.add_argument(
        "--weight-attribute",
        default="FamilyWeight",
        help="The GML edge attribute to be used as edge weight."
        " (default: FamilyWeight.)")
    parameters.add_argument(
        "--concept-weight", choices=list(concept_weights),
        default="square",
        help="The weight of a concept, as function of its degree."
        " (default: square.)")
    parameters.add_argument(
        "--seed", type=int,
        default=0,
        help="The random number generator seed (default: 0)")
    tree = parser.add_argument_group(
        "Shape of the phylogeny")
    tree.add_argument(
        "--tree",
        help="A phylogenetic tree to be simulated in Newick format, or the"
        " path to an existing file containing such a tree. (default: A single"
        " long branch with nodes after 0, 1, 2, 4, 8, …, 2^N time steps.)")
    tree.add_argument(
        "--branchlength", type=int,
        default=28,
        help="If no tree is given, the log₂ of the maximum branch length"
        " of the long branch, i.e. N from the default value above."
        " (default: 20.)")
    processing = parser.add_argument_group(
        "Processing")
    processing.add_argument(
        "--resume", action="store_true",
        default=False,
        help="Resume a run from a previous partial output")
    processing.add_argument(
        "--multiprocess", type=int,
        default=1,
        help="The number of parallel processes to run.")
    output = parser.add_argument_group(
        "Output")
    output.add_argument(
        "--output", type=argparse.FileType("w"),
        default=tempfile.mkstemp()[0],
        help="The file to write output data to (in CLDF-like CSV)."
        " (default: A temporary file.)")
    output.add_argument(
        "--embed-parameters", action="store_true",
        default=False,
        help="Echo the simulation parameters to comments in the CSV output"
        " file.")
    return parser


def phylogeny(args):
    if args.tree is None:
        tree = newick.Node("0")
        parent = tree
        length = 0
        for i in range(args.branchlength + 1):
            new_length = 2 ** i
            child = newick.Node(
                str(new_length),
                str(new_length - length))
            parent.add_descendant(child)
            parent = child
            length = new_length
    else:
        try:
            file = Path(args.tree).open()
            tree = newick.load(file)[0]
        except (OSError, FileNotFoundError):
            if ":" in args.tree or "(" in args.tree:
                tree = newick.loads(args.tree)[0]
            else:
                raise ValueError(
                    "Argument for --tree looked like a filename, not like a"
                    " Newick tree, but no such file could be opened.")
    args.tree = tree.newick
    return tree


def echo(args):
    for arg, value in args.__dict__.items():
        if arg == "embed_parameters":
            continue
        if arg == "output_file":
            continue
        if arg == "multiprocess":
            continue
        if arg == "resume":
            continue
        if arg == "root_language_data":
            continue
        if arg == "phylogeny":
            continue
        if arg == "simulator":
            continue
        if value is not None:
            try:
                value = value.name
            except AttributeError:
                pass
            yield arg, value


def read_wordlist(wordlist, semantics,
                  only_language=None, all_languages=False, weight=100):
    languages = collections.OrderedDict()
    with UnicodeDictReader(
            wordlist, dialect=Dialect(commentPrefix="#")) as reader:
        for line in reader:
            language_id = line["Language_ID"]
            if (only_language and language_id != only_language):
                continue
            concept = line["Parameter_ID"]
            try:
                wt = int(line["Weight"])
            except KeyError:
                wt = weight()
            if language_id not in languages:
                languages[language_id] = Language({}, semantics)
            word = int(line["Cognateset_ID"])
            languages[language_id][concept][word] = wt
            Language.max_word = max(Language.max_word, word)
    if all_languages:
        return languages
    else:
        if only_language is None:
            only_language = list(languages)[-1]
        return languages[only_language]


class concept_weight:
    def __init__(self, weight, semantics):
        self.weight = weight
        self.semantics = semantics

    def __call__(self, concept):
        return concept_weights[self.weight](len(self.semantics[concept]))


def prepare(parser):
    args = parser.parse_args()

    simulator = simulate
    if args.multiprocess != 1:
        simulator = Multiprocess(args.multiprocess).simulate
    if args.resume:
        simulator = Multiprocess(args.multiprocess).simulate_remainder

    weight = parse_distribution_description(
        args.weight,
        random=numpy.random.RandomState(args.seed))

    args.phylogeny = phylogeny(args)

    if args.semantic_network:
        semantics = SemanticNetworkWithConceptWeight.load_from_gml(
            args.semantic_network, args.weight_attribute)
    else:
        semantics = SemanticNetworkWithConceptWeight.load_from_gml(
            default_network.open(),
            args.weight_attribute)
    semantics.neighbor_factor = args.neighbor_factor

    semantics.concept_weight = concept_weight(args.concept_weight,
                                              semantics)

    if args.resume:
        mp = Multiprocess(args.multiprocess)
        resume_from = mp.generated_languages
        simulator = mp.simulate_remainder
        # Resuming when the root language is not available doesn't make any
        # sense, so fill the root language with a nonsense value that will
        # raise an error later. FIXME: Make the later error message more
        # transparent.
        for language_id, language in read_wordlist(
                args.wordlist, semantics,
                all_languages=True, weight=weight).items():
            resume_from[language_id] = language
        args.root_language_data = None
    elif args.wordlist:
        args.root_language_data = read_wordlist(
            args.wordlist, semantics, args.language, weight=weight)
    else:
        raw_language = {
            concept: collections.defaultdict(
                constant_zero, {c: weight()})
            for c, concept in enumerate(semantics)}
        args.root_language_data = Language(raw_language, semantics)

    args.simulator = simulator
    return args


def run_and_write(args):
    with CommentedUnicodeWriter(
            args.output, commentPrefix="# ") as writer:
        writer.writerow(
            ["Language_ID", "Parameter_ID", "Cognateset_ID", "Weight"])
        if args.embed_parameters:
            for arg, value in echo(args):
                writer.writecomment(
                    "--{:s} {:}".format(
                        arg, value))
        for id, data in args.simulator(
                args.phylogeny, args.root_language_data,
                seed=args.seed,
                writer=writer):
            print("Language {:} generated.".format(id))
            yield id, data
