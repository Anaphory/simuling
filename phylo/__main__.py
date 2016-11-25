import argparse


from .cli import run, basic_vocabulary_sampler_of_size
from .language import Language


parser = argparse.ArgumentParser(description=""" Run a very simple forward-time
phylogenetic simulation of cognate class evolution in a language
family.""")
parser.add_argument(
    '-t', type=int, default=100,
    help="Number of simulations to run with the same concept graph")

group = parser.add_argument_group("Shared properties of the languages")
group.add_argument('-s', type=int, default=2000,
                   help="Number of concepts to be simulated")
group.add_argument('-f', type=int, default=50,
                   help="Number of semantic fields the concepts show")
group = parser.add_argument_group("Properties of the phylogenetic simulation")
group.add_argument("-l", type=str, nargs="+", default=list("ABCDEFGHIJKLMN"),
                   help="Taxon names")
group.add_argument('--max', type=int, default=11000,
                   help="Minimum number of change events along a branch")
group.add_argument('--min', type=int, default=9000,
                   help="Maximum number of change events along a branch")
group.add_argument('--p-lose', type=float, default=0.5,
                   help="Probability, per time step, that a word becomes "
                   "less likely for a meaning")
group.add_argument('--p-gain', type=float, default=0.4,
                   help="Probability, per time step, that a word gains a "
                   "related meaning")
group.add_argument('--p-new', type=float, default=0.1,
                   help="Probability, per time step, that a new word arises")
group.add_argument("--tree", default="simulation",
                   help="Filename to write the tree to. "
                   "'-{run_number:}.tre is appended automatically.")
group = parser.add_argument_group("Wordlist sampling")
group.add_argument(
    "-r", "--sample-all-roots",
    action='append_const', dest='sampler', const=("r", Language.all_reflexes))
group.add_argument(
    "-b", "--sample-basic-wordlist-size",
    type=basic_vocabulary_sampler_of_size,
    action='append', dest='sampler',
    help="Add a basic wordlist sampler for vocabulary size B")
group.add_argument(
    '--wordlist', type=str, default="simulation",
    help="Filename to write the word lists to. "
    "'-{sampler:}-{run_number:}.tsv' is appended automatically.")


args = parser.parse_args()
if args.sampler is None:
    args.sampler = [basic_vocabulary_sampler_of_size(200)]


run(times=args.t,
    signs=args.s,
    fields=args.f,
    taxa=args.l,
    change_range=args.max,
    change_min=args.min,
    wordlist_filename=args.wordlist,
    tree_filename=args.tree,
    samplers=args.sampler)
