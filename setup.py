#!/usr/bin/env python

from setuptools import setup

setup(
    name="simuling",
    version="0.1",
    description="Forward-time stochastic simulation of word/meaning coupling",
    author="Gereon Kaiping",
    author_email="g.a.kaiping@hum.leidenuniv.nl",
    url="http://github.com/Anaphory/simuling",
    packages=["simuling", "phylo"],
    entry_points={
        'console_scripts' : ['phylo=phylo.cli:main'],
        },
    install_requires=[
        "networkx",
        "lingpy",
        "numpy",
        "pytest",
        "pytest-cov",
        "pytest-pep8",
        "sumatra",
        "gitpython",
        ])
