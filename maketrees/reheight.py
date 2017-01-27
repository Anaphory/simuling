#!/usr/bin/env python

import argparse

import newick


def normalize_tree(root):
    """Ensure all leaves of the tree have equal depth.

    To get that, recursively average lengths.

    """
    heights = []
    subtrees = []
    for node in root.descendants:
        height, subtree = normalize_tree(node)
        heights.append(height)
        subtrees.append(subtree)
    if heights:
        height = sum(heights)/len(heights)
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
    parser.add_argument("--output", "-o", type=argparse.FileType('w'))

    args = parser.parse_args()
    trees = newick.load(args.trees)
    for tree in trees:
        normalize_tree(tree)
