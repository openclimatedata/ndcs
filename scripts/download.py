# encoding: UTF-8

import urllib.request
import csv

from countrygroups import EUROPEAN_UNION as eu28
from pathlib import Path

root = Path(__file__).parents[1]
pdfs_dir = root / "pdfs"
ndcs = root / "data/ndcs.csv"

if not pdfs_dir.exists():
    pdfs_dir.mkdir()

with open(str(ndcs), "r") as csvfile:
    ndcreader = csv.DictReader(csvfile)
    for row in ndcreader:
        is_eu_member = (row["Filename"].startswith("EUU_European-Union") and
                        row["Code"] in eu28)
        if is_eu_member:
            print("Skipping {}: EU member".format(row["Party"]))
            continue
        filename = pdfs_dir / row["Filename"]
        if filename.exists():
            print("Already downloaded: {}".format(row["Filename"]))
            continue
        print(row["Filename"], "<=", row["OriginalFilename"])
        url = urllib.parse.urlsplit(row["EncodedAbsUrl"])
        url = list(url)
        url[2] = urllib.parse.quote(urllib.parse.unquote(url[2]))
        url = urllib.parse.urlunsplit(url)
        urllib.request.urlretrieve(url)

        urllib.request.urlretrieve(url, filename)
