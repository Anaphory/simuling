#!/usr/bin/env python

"""Install the simuling package."""

from setuptools import setup

setup(
    name="simuling",
    version="0.2",
    description="Forward-time stochastic simulation of word/meaning coupling",
    author="Gereon Kaiping",
    author_email="g.a.kaiping@hum.leidenuniv.nl",
    url="http://github.com/Anaphory/simuling",
    packages=["simuling"],
    entry_points={
        'console_scripts': ['phylo=phylo.__main__'],
    },
    install_requires=[
        "networkx",
        "matplotlib",
        "lingpy",
        "numpy",
        "pandas",
        "pytest",
        "pycldf",
        "pytest-cov",
        "pytest-pep8",
        "sumatra",
        "gitpython",
        "biopython",
        "newick",
    ])
