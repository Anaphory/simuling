import os
import json
import itertools

from ..cli import read_wordlist


def shared_vocabulary(l1, l2, threshold=4):
    """Calculate the proportion of shared items between two languages.

    For the pair of languages which are sampled in `vocab1` and `vocab2`,
    calculate how many cognate-meaning pairs they share. Multiple cognates in
    one meaning slot are counted as |C∩D|/|C∪D|, which is a generalization of
    picking 0 when the sets of cognates are disjoint and 1 when they match
    exactly.

    """
    score = 0
    features = set(l1) | set(l2)
    n_features = 0
    for feature in features:
        cognateset1 = set(word
                          for word, weight in l1[feature].items()
                          if threshold is None or weight > threshold)
        cognateset2 = set(word
                          for word, weight in l2[feature].items()
                          if threshold is None or weight > threshold)
        if cognateset1 | cognateset2:
            # Due to the filtering, this can end up empty
            score += (len(cognateset1 & cognateset2) /
                      len(cognateset1 | cognateset2))
            n_features += 1
    return score / n_features


def cached_realdata(data):
    try:
        with open(os.path.join(
                os.path.dirname(__file__),
                "pairwise_shared_vocabulary.json")) as realdata_cache:
            realdata = json.load(realdata_cache)
        realdata_cache_filename = realdata.pop("FILENAME")
        if realdata_cache_filename != data.name:
            raise ValueError("Cached filename mismatches data file")
    except (FileNotFoundError, ValueError):
        languages = read_wordlist(data, None, all_languages=True,
                                  weight=lambda: 10)
        for (l1, vocabulary1), (l2, vocabulary2) in (
                itertools.combinations(languages.items(), 2)):
            # Normalize the key, that is, the pair (l1, l2)
            if l1 > l2:
                l1, l2 = l2, l1
            score = shared_vocabulary(vocabulary1, vocabulary2)
            realdata[" ".join((l1, l2))] = score
        realdata["FILENAME"] = data.name
        with open(os.path.join(
                os.path.dirname(__file__),
                "pairwise_shared_vocabulary.json"), "w") as realdata_cache:
            json.dump(realdata, realdata_cache)
        realdata_cache_filename = realdata.pop("FILENAME")
    return {tuple(key.split()): value for key, value in realdata.items()}
