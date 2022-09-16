# encoding: UTF-8

import urllib.request
import csv

from countrygroups import EUROPEAN_UNION as EU
from pathlib import Path

root = Path(__file__).parents[1]
pdfs_dir = root / "pdfs"
ndcs = root / "data/ndcs.csv"

if not pdfs_dir.exists():
    pdfs_dir.mkdir()

with open(str(ndcs), "r") as csvfile:
    ndcreader = csv.DictReader(csvfile)
    for row in ndcreader:
        if row["Code"] in EU:
            print("Skipping {}: EU member".format(row["Party"]))
            continue
        filename = pdfs_dir / row["OriginalFilename"]
        if filename.exists():
            print("Already downloaded: {}".format(row["OriginalFilename"]))
            continue
        print(f"Fetching {row['OriginalFilename']}")
        url = urllib.parse.urlsplit(row["EncodedAbsUrl"])
        url = list(url)
        url[2] = urllib.parse.quote(urllib.parse.unquote(url[2]))
        url = urllib.parse.urlunsplit(url)
        urllib.request.urlretrieve(url)

        urllib.request.urlretrieve(url, str(filename))
