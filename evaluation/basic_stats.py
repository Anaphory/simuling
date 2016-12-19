"""Calculate various stats for the languages in the sample.

Provide functions to calculate weighted average number of synonyms, of
meaning spread, etc. for each language in a given TSV file.

"""

import pandas


def synonymity(data):
    """Calculate average synonym count.

    Calculate the average weighted synonym count in the language
    represented by data.

    """
    syn = 0
    m = 0
    for meaning, words in data.groupby("Feature_ID"):
        syn += words["Weight"].sum()**2/(words["Weight"]**2).sum()
        m += 1
    return syn/m


def vocabulary_size(data):
    """Count different words in vocabulary."""
    return len(set(data["Global_CogID"]))


def semantic_width(data):
    """Calculate average synonym count.

    Calculate the average weighted semantic width in the language
    represented by data.

    """
    width = 0
    m = 0
    for form, meanings in data.groupby("Global_CogID"):
        width += meanings["Weight"].sum()**2/(meanings["Weight"]**2).sum()
        m += 1
    return width/m


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Calculate language statistics")
    parser.add_argument("filename", type=argparse.FileType('r'), nargs="+",
                        help="Path to the wordlist CLDF TSV file.")
    args = parser.parse_args()

    for filename in args.filename:
        all_data = pandas.read_csv(
            filename,
            sep="\t",
            na_values=[""],
            keep_default_na=False,
            encoding='utf-8')

        for language_id, language_data in all_data.groupby("Language_ID"):
            print("\t".join(map(str, [filename.name,
                                      language_id,
                                      synonymity(language_data),
                                      semantic_width(language_data),
                                      vocabulary_size(language_data)])))
