#!/usr/bin/env python

import pytest

from speaker import *


@pytest.fixture
def speaker():
    return Speaker()


def test_guess(speaker):
    values = {"a": {'weight': 4}, "b": {'weight': 1}}
    counter = {x: 0 for x in values.keys()}
    k = 10000
    weight_sum = sum([i['weight'] for i in values.values()])
    for _ in range(weight_sum*k):
        counter[speaker.guess(values)] += 1
    for key, val in counter.items():
        assert k*values[key]['weight']*0.9 < val < k*values[key]['weight']/0.9
