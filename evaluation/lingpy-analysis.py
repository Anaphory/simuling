from lingpy import *
from lingpy.basic.wordlist import get_wordlist
from pyconcepticon.api import Concepticon

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
    parser.add_argument(
        '--mode', default='jaccard')
    parser.add_argument(
        '--sublist', action='store_true', default=False)
    parser.add_argument(
        '--sublistname', default='Swadesh-1955-100')
    args = parser.parse_args()

    # get the swadesh list
    cnc = Concepticon()
    swadesh_ = cnc.conceptlists[args.sublistname].concepts
    swadesh = {
            swadesh_[idx].concepticon_gloss: swadesh_[idx].concepticon_id
            for idx in swadesh_.keys()}

    wl = get_wordlist(
        args.infile, col='language_id',
        row='feature_id', delimiter='\t')
    if args.sublist:
        D = {
                0: [
                    h for h in sorted(
                        wl.header, key=lambda x: wl.header[x])]
                }
        for k, concept in iter_rows(wl, 'feature_id'):
            if concept in swadesh:
                D[k] = wl[k]
        wl = Wordlist(D, col='language_id', row='feature_id')

    ref = 'global_cogid'
    if args.sampling != 'etyma':
        wl.add_entries(
            'paps', 'value,feature_id',
            lambda x, y: str(x[y[0]]) + '-' + str(x[y[1]]))
        ref = 'paps'

    wl.calculate(
        'tree', taxa='language_id', concepts='feature_id',
        tree_calc=args.method, ref=ref, distances=True, mode=args.mode)
    print(wl.tree)
