# Tree Comparison Methods

This directory contains methods for comparing trees. The purpose is to
provide a simple interface to various methods of calculating distances
and similarities between original and reconstructed trees, or trees
reconstructed using different methods.

A typical script here looks like this.

    usage: distance.py [-h] [--output OUTPUT]
                       [--distance {method1,method2}]
                       original reconstructed
                       
It takes two files containing Newick trees as input. Either `original`
contains only one tree, leading to a 1:n comparison, or the script
will assume that there is a 1:1 correspondence between the lines in
original and reconstructed, ignoring lines in one file after the end
of the other. It will then calculate some number measuring similarity
(bigger=more similar) or distance (0=identical, smaller=more similar)
and write one such measure for each pair, either to the OUTPUT path
provided or to stdout.

The calculation method can be selected using `--distance`, there may
be other command line switches.

