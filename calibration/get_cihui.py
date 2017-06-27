#!/usr/bin/env python3

"""Get Cihui data for calibration from repository."""

import os
import pandas

import urllib.request

ROOT = "https://raw.githubusercontent.com/digling/cddb/master/"
for (file, source) in [
        ("beijingdaxue1964.csv", ROOT + "datasets/BeijingDaxue1964/cldf/"),
        ("dated.tre", ROOT + "datasets/BeijingDaxue1964/trees/")]:
    local = os.path.join(os.path.dirname(__file__), file)
    if os.path.isfile(local):
        continue

    urllib.request.urlretrieve(source+file, local)

    if file == "beijingdaxue1964.csv":
        with_nans = pandas.read_csv(local)
        nans = pandas.isnull(with_nans["Parameter_ID"])
        with_nans["Parameter_ID"][nans] = with_nans["Parameter_name"][nans]

        with_nans.to_csv(local)
