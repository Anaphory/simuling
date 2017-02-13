#!/usr/bin/env python

"""Subsample a wordlist according to existing sampling methods.

Provide a CLI to sub-sample word lists according to the lists
Concepticon is based on.

"""

import argparse
import sys

from lingpy.basic.wordlist import get_wordlist


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "calculate phylogenetic trees with simple distance methods")
    parser.add_argument(
        'infile', nargs='?', default=sys.stdin, help='your wordlist file')
    parser.add_argument(
        '--output', '-o', default=sys.stdout)
    parser.add_argument(
        '-m', '--method', default='neighbor')
    parser.add_argument(
        '--mode', default='jaccard')
    args = parser.parse_args()

    wl = get_wordlist(
        args.infile, col='language_id',
        row='feature_id', delimiter=',')

    ref = 'value'

    wl.calculate(
        'tree', taxa='language_id', concepts='feature_id',
        tree_calc=args.method, ref=ref, distances=True, mode=args.mode)
    print(wl.tree)
