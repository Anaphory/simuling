"""Simulate lexical evolution based on gradual semantic shift.

"""

import argparse
import tempfile
from pathlib import Path

import newick


concept_weights = {
    "one": lambda degree: 1,
    "degree": lambda degree: degree,
    "square": lambda degree: degree ** 2,
    "exponential": lambda degree: 2 ** degree}


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
        default=20,
        help="If no tree is given, the log₂ of the maximum branch length"
        " of the long branch, i.e. N from the default value above."
        " (default: 20.)")
    output = parser.add_argument_group(
        "Output")
    output.add_argument(
        "--output-file", type=argparse.FileType("w"),
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
        phylogeny = newick.Node("0")
        parent = phylogeny
        length = 0
        for i in range(args.branchlength + 1):
            new_length = 2 ** i
            child = newick.Node(
                str(new_length),
                str(new_length - length))
            parent.add_descendant(child)
            parent = child
            length = new_length
    elif Path(args.tree).exists:
        phylogeny = newick.load(Path(args.tree).open())[0]
    elif ":" in args.tree or "(" in args.tree:
        phylogeny = newick.loads(args.tree)[0]
    else:
        raise ValueError(
            "Argument for --tree looked like a filename, not like a Newick"
            "tree, but no such file exists.")
    args.tree = phylogeny.newick
    return phylogeny


def echo(args):
    for arg, value in args.__dict__.items():
        if arg == "embed_parameters":
            continue
        if arg == "output_file":
            continue
        if value is not None:
            try:
                value = value.name
            except AttributeError:
                pass
            yield arg, value
