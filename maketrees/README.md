# Tree Generation Methods

This directory contains methods for generating and modifying trees
from scratch (or from other trees). The purpose is to provide methods
to generate random trees, and to modify trees (prune, scale, …) before
running simulations on them.

Luke Maurits' `phyltr` (https://github.com/lmaurits/phyltr) may be
useful in this context.

A typical script in here either 

(a) generates `-t T` Newick trees according to some method and writes
    them to stdout or an `-o`/`--output` filename provided, or

(b) reads trees in Newick format from an input file (default: stdin),
    transforms each one in some way, and writes them to stdout or an
    `-o`/`--output` filename provided.

Such a tree file can then be used as input to the `phylo` package.
