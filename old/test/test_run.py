#!/usr/bin/env python

"""Test command line interface functionality."""

import pytest

import io

import simuling.phylo.__main__ as run


def test_empty_argparser():
    """Check that argparser complains about lack of CLI arguments."""
    with pytest.raises(SystemExit):
        run.argparser([])


def test_argparser():
    """Check that argparser runs when given a tree."""
    run.argparser(["-"])


def test_run_trivial_no_output_check():
    """Check that the main simulation runner runs.

    Do not check the results it generates.

    """
    args = run.argparser(["-"])
    args.trees = [io.StringIO("(A:1,B:3):4")]
    args.wordlist = "-"
    run.run_simulation_with_arguments(args)
