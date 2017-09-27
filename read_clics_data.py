from collections import Counter

import numpy
import pandas

from clldutils.path import Path

CLICS_DATA = Path('../devel/clics-data/cldf')

vocabularies, features, synonymies, polysemies = {}, {}, {}, {}
concepts = set()
for dataset in CLICS_DATA.iterdir():
    if not dataset.is_dir():
        continue

    for file in dataset.iterdir():
        if file.suffix == '.csv':
            data = pandas.read_csv(file)
        elif file.suffix == '.tsv':
            data = pandas.read_csv(file, sep='\t')
        else:
            continue

        concepts |= set(data['Parameter_ID'])
        for doculect, vocabulary in data.groupby('Doculect_id'):
            slots = len(set(vocabulary['Parameter_ID']))
            features[doculect] = slots
            vocabularies[doculect] = len(set(vocabulary['Clics_Value']))
            synonymy = Counter()
            for meaning, words in vocabulary.groupby('Parameter_ID'):
                synonymy[len(set(words['Clics_Value']))] += 1
            synonymies[doculect] = synonymy
            polysemy = Counter()
            for word, meanings in vocabulary.groupby('Clics_Value'):
                polysemy[len(set(meanings['Parameter_ID']))] += 1
            polysemies[doculect] = polysemy


print("Doculects:", len(vocabularies))
print("Concepts:", len(concepts))
print("Concept slots:",
      numpy.mean(list(features.values())),
      "±", numpy.std(list(features.values())))
print("Word forms:",
      numpy.mean(list(vocabularies.values())),
      "±", numpy.std(list(vocabularies.values())))
syn_per = sum(synonymies.values(), Counter())
avg_syn = sum(w*f for w, f in syn_per.items()) / sum(syn_per.values())
print("Synonyms:", avg_syn)
concs_per = sum(polysemies.values(), Counter())
avg_pol = sum(w*f for w, f in concs_per.items()) / sum(concs_per.values())
print("Polysemy:", avg_pol)
print("Expected complete word list:", avg_syn/avg_pol*len(concepts))
