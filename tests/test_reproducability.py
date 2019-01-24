import json
from pathlib import Path
import newick
import tempfile
import numpy.random
from csvw import UnicodeWriter

import pytest

import simuling.simulation as s
from simuling.cli import read_wordlist


@pytest.fixture(scope="module")
def data_cache():
    try:
        trace = Path(__file__).parent / "trace.json"
        data = json.load(trace.open())
    except FileNotFoundError:
        data = {}
    yield data
    json.dump(data, trace.open("w"))


def test_random_concept(data_cache):
    nw = s.SemanticNetwork(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]})
    random = numpy.random.RandomState(2)
    r1 = nw.random(random)
    random = numpy.random.RandomState(2)
    r2 = nw.random(random)
    assert r1 == r2
    try:
        assert r1 == data_cache["random_concept"]
    except KeyError:
        data_cache["random_concept"] = r1
    except AssertionError:
        data_cache["random_concept"] = r1
        raise


def test_weighted_random_concept(data_cache):
    nw = s.SemanticNetworkWithConceptWeight(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]},
        concept_weight=lambda x: 1/x)
    random = numpy.random.RandomState(2)
    r1 = nw.random(random)
    random = numpy.random.RandomState(2)
    r2 = nw.random(random)
    assert r1 == r2
    try:
        assert r1 == data_cache["weighted_random_concept"]
    except KeyError:
        data_cache["weighted_random_concept"] = r1
    except AssertionError:
        data_cache["weighted_random_concept"] = r1
        raise


def test_language_random_edge(data_cache):
    nw = s.SemanticNetwork(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]})
    root = s.Language({"c1": {1: 4}, "c5": {2: 4}}, nw)
    random = numpy.random.RandomState(2)
    e1 = root.random_edge(random)
    random = numpy.random.RandomState(2)
    e2 = root.random_edge(random)
    assert e1 == e2
    try:
        assert list(e1) == data_cache["random_language_edge"]
    except KeyError:
        data_cache["random_language_edge"] = e1
    except AssertionError:
        data_cache["random_language_edge"] = e1
        raise


def test_language_step(data_cache):
    nw = s.SemanticNetwork(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]})
    l1 = s.Language({"c1": {1: 1}, "c5": {5: 5}}, nw)
    l2 = l1.copy()

    random = numpy.random.RandomState(2)
    l1.step(random)
    random = numpy.random.RandomState(2)
    l2.step(random)
    assert str(l1) == str(l2)
    try:
        assert str(l1) == data_cache["language_step"]
    except KeyError:
        data_cache["language_step"] = str(l1)
    except AssertionError:
        data_cache["language_step"] = str(l1)
        raise


def test_simulate(data_cache):
    phylogeny = newick.loads('(A:2,B:1)C;')[0]
    nw = s.SemanticNetwork(
        {"1": ["2"], "2": ["3"], "4": ["2"], "5": ["4"]})
    l1 = s.Language({"c1": {1: 4}, "c5": {2: 4}}, nw)
    l2 = l1.copy()

    languages1 = {}
    for name, language in s.simulate(phylogeny, l1, seed=0):
        languages1[name] = str(language)

    languages2 = {}
    for name, language in s.simulate(phylogeny, l2, seed=0):
        languages2[name] = str(language)

    assert languages1 == languages2
    try:
        assert str(languages1) == data_cache["simulate"]
    except KeyError:
        data_cache["simulate"] = str(languages1)
    except AssertionError:
        data_cache["simulate"] = str(languages1)
        raise


def test_multiprocess(data_cache):
    phylogeny = newick.loads('(A:2,B:2)C:2;')[0]
    nw = s.SemanticNetwork(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]})
    l1 = s.Language({"c1": {1: 4}, "c5": {2: 4}}, nw)
    l2 = l1.copy()

    languages1 = {}
    for name, language in s.simulate(phylogeny, l1, seed=0):
        languages1[name] = str(language)

    print()
    languages2 = {}
    process = s.Multiprocess(2)
    for name, language in process.simulate_remainder(phylogeny, l2, seed=0):
        languages2[name] = str(language)

    assert languages1 == languages2
    try:
        assert str(languages1) == data_cache["multiprocess"]
    except KeyError:
        data_cache["multiprocess"] = str(languages1)
    except AssertionError:
        data_cache["multiprocess"] = str(languages1)
        raise


def test_write_and_resume(data_cache):
    phylogeny = newick.loads('(A:2)C:2;')[0]
    nw = s.SemanticNetwork(
        {"c1": ["c2"], "c2": ["c3"], "c4": ["c2"], "c5": ["c4"]})
    l1 = s.Language({"c1": {1: 4}, "c5": {2: 4}}, nw)
    l2 = l1.copy()

    languages1 = {}
    for name, language in s.simulate(phylogeny, l1, seed=0):
        languages1[name] = str(language)

    print()
    languages2 = {}
    process = s.Multiprocess(2)
    with tempfile.TemporaryFile('w+') as f:
        with UnicodeWriter(f) as writer:
            writer.writerow(
                ["Language_ID", "Parameter_ID", "Cognateset_ID", "Weight"])
            for name, language in process.simulate(phylogeny, l2, seed=0,
                                                   writer=writer):
                break

        f.seek(0)
        wordlist = read_wordlist(f, nw, all_languages=True)
        process = s.Multiprocess(2)
        process.generated_languages.update(wordlist)
        for name, language in process.simulate_remainder(phylogeny):
            languages2[name] = str(language)

    assert languages1 == languages2
    try:
        assert str(languages1) == data_cache["write_resume"]
    except KeyError:
        data_cache["write_resume"] = str(languages1)
    except AssertionError:
        data_cache["write_resume"] = str(languages1)
        raise
