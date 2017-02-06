#!/usr/bin/env python

"""Subsample a wordlist according to existing sampling methods.

Provide a CLI to sub-sample word lists according to the lists
Concepticon is based on.

"""

from lingpy import Wordlist, iter_rows
from lingpy.basic.wordlist import get_wordlist
from pyconcepticon.api import Concepticon

import argparse
import sys

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
        '-s', '--sampling', default='etyma')
    parser.add_argument(
        '--mode', default='jaccard')
    parser.add_argument(
        '--sublist', action='store_true', default=False)
    parser.add_argument(
        '--sublistname', default='Swadesh-1955-100')
    parser.add_argument(
        '--removesynonyms', default=False, action='store_true')
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

    blacklist = []
    if args.removesynonyms:
        blacklist = []
        for taxon in wl.cols:
            tmp = wl.get_dict(col=taxon)
            for c, idxs in tmp.items():
                weights = [int(wl[idx, 'weight']) for idx in idxs]
                all_weights = sum(weights)
                min_weight = all_weights * 0.25
                for idx, weight in zip(idxs, weights):
                    if weight < min_weight:
                        blacklist += [idx]

    if args.sublist:
        D = {
                0: [
                    h for h in sorted(
                        wl.header, key=lambda x: wl.header[x])]
                }
        for k, concept in iter_rows(wl, 'feature_id'):
            if concept in swadesh and k not in blacklist:
                D[k] = wl[k]
        wl = Wordlist(D, col='language_id', row='feature_id')

    ref = 'global_cogid'
    if args.sampling != 'etyma':
        ref = 'concept_cogid'

    wl.calculate(
        'tree', taxa='language_id', concepts='feature_id',
        tree_calc=args.method, ref=ref, distances=True, mode=args.mode)
    print(wl.tree)
