#!/usr/bin/env python


def iterate_wordlist_rows(wordlist, *columns):
    if not columns:
        columns = range(len(wordlist._header))
    else:
        columns = [wordlist._header[wordlist._alias[col]] for col in columns]

    for key in wordlist:
        row = wordlist[key]
        yield [row[i] for i in columns]


def semantic_width(wordlist, cognate_column="cogid", concept_column="concept"):
    """Calculate how many concepts a cognate class encompasses, on average

    Parameters
    ----------

    wordlist: lingpy.Wordlist

    cognate_column: string (default = "cogid")
        The name of a column of `wordlist` representing cross-concept
        congnate classes.

    concept_column: string (default = "concept")
        The name of a column of `wordlist` listing concepts.

    Returns
    -------
    average_semantic_width: float
        The average cross-linguistic semantic width of a concept.

    """

    concepts_per_cognate = {}
    for concept, cogids in iterate_wordlist_rows(
            wordlist, concept_column, cognate_column):
        try:
            cogids = set(cogids)
        except TypeError:
            cogids = [cogids]

        for cogid in cogids:
            concepts_per_cognate.setdefault(
                cogid,
                set()).add(concept)

    if not concepts_per_cognate:
        return float('nan')
    return sum(len(x)
               for x in concepts_per_cognate.values()) / len(
        concepts_per_cognate)
