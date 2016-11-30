from lingpy import *
from lingpy.basic.wordlist import get_wordlist

import argparse
import sys

if __name__ == '__main__':
    from sys import argv
    parser = argparse.ArgumentParser(
            "calculate phylogenetic trees with simple distance methods")
    parser.add_argument(
            'infile', nargs='?', default=sys.stdin, help='your wordlist file')
    parser.add_argument(
            '--output', '-o', default=sys.stdout)
    parser.add_argument(
            '-m', '--method', default='neighbor')
    parser.add_argument(
            '-s', '--sampling', default='etyma')
    args = parser.parse_args()
    wl = get_wordlist(
            args.infile, col='language_id',
            row='feature_id', delimiter=',')
    ref = 'value'
    if args.sampling != 'etyma':
        wl.add_entries(
                'paps', 'value,feature_id',
                lambda x, y: str(x[y[0]])+'-'+str(x[y[1]]))
        ref = 'paps'

    wl.calculate(
            'tree', taxa='language_id', concepts='feature_id',
            method=args.method, ref=ref, distances=True)
    print(wl.tree)
