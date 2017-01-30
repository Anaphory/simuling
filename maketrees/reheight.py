#!/usr/bin/env python

import argparse
import sys

import newick


def normalize_tree(root, mean=lambda x: sum(x)/len(x)):
    """Ensure all leaves of the tree have equal depth.

    To get that, recursively average lengths.

    """
    heights = []
    subtrees = []
    for node in root.descendants:
        height, subtree = normalize_tree(node, mean)
        heights.append(height)
        subtrees.append(subtree)
    if heights:
        height = mean(heights)
        for node, ht in zip(subtrees, heights):
            if ht-node.length > height:
                height = ht-node.length
        for node, ht in zip(subtrees, heights):
            node.length += height-ht
        return root.length + height, root
    return root.length, root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trees", type=argparse.FileType('r'))
    parser.add_argument("--output", "-o",
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="Output filename")
    parser.add_argument(
        "--mean", action="store_const", dest="acc",
        const=lambda x: sum(x)/len(x), default=lambda x: sum(x)/len(x),
        help="Use arithmetic mean to calculate new branch height")
    parser.add_argument(
        "--rms", action="store_const", dest="acc",
        const=lambda x: (sum(map(lambda xi: xi*xi, x))/len(x))**0.5,
        help="Use root mean square to calculate new branch height")
    parser.add_argument(
        "--max", action="store_const", dest="acc",
        const=max,
        help="Use maximum to calculate new branch height")

    args = parser.parse_args()
    trees = newick.load(args.trees)
    for tree in trees:
        normalize_tree(tree, args.acc)
    newick.dump(trees, args.output)
