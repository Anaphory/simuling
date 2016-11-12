import argparse


from .cli import run


parser = argparse.ArgumentParser(description=""" Run a very simple forward-time
phylogenetic simulation of cognate class evolution in a language
family.""")
parser.add_argument('-t', type=int, default=100)
parser.add_argument('--max', type=int, default=2000)
parser.add_argument('--min', type=int, default=1900)
parser.add_argument('-s', type=int, default=1000)
parser.add_argument('-f', type=int, default=50)
parser.add_argument("-l", type=list, default="ABCDEFGHIJKLMN")
parser.add_argument('-b', type=int, default=200)


args = parser.parse_args()
run(times=args.t,
    signs=args.s,
    fields=args.f,
    taxa=args.l,
    change_range=args.max,
    change_min=args.min,
    basic_list=range(args.b))
