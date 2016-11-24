import argparse


from .cli import run


parser = argparse.ArgumentParser(description=""" Run a very simple forward-time
phylogenetic simulation of cognate class evolution in a language
family.""")
parser.add_argument(
    '-t', type=int, default=100,
    help="Number of simulations to run with the same concept graph")
parser.add_argument('--max', type=int, default=11000,
                    help="Minimum number of change events along a branch")
parser.add_argument('--min', type=int, default=9000,
                    help="Maximum number of change events along a branch")
parser.add_argument('-s', type=int, default=2000,
                    help="Number of concepts to be simulated")
parser.add_argument('-f', type=int, default=50,
                    help="Number of semantic fields the concepts show")
parser.add_argument("-l", type=list, default="ABCDEFGHIJKLMN",
                    help="Taxon names")
parser.add_argument('-b', type=int, default=200,
                    help="Basic vocabulary size to be sampled")
parser.add_argument('--wordlist', type=str, default=None,
                    help="Filename to write the word lists to. "
                    "'{:run_number}.tsv' is appended automatically.")
parser.add_argument('--p-lose', type=float, default=0.5,
                    help="Probability, per time step, that a word becomes "
                    "less likely for a meaning")
parser.add_argument('--p-gain', type=float, default=0.4,
                    help="Probability, per time step, that a word gains a "
                    "related meaning")
parser.add_argument('--p-new', type=float, default=0.1,
                    help="Probability, per time step, that a new word arises")


args = parser.parse_args()
run(times=args.t,
    signs=args.s,
    fields=args.f,
    taxa=args.l,
    change_range=args.max,
    change_min=args.min,
    wordlist_filename=args.wordlist,
    basic_list=range(args.b))
