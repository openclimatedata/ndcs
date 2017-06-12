# encoding: UTF-8

import os
import unicodedata
import urllib.request
import csv

path = os.path.dirname(os.path.realpath(__file__))
pdfs_dir = os.path.join(path, "../pdfs/")
ndcs = os.path.join(path,  "../data/ndcs.csv")

if not os.path.exists(pdfs_dir):
    os.makedirs(pdfs_dir)

eu28 = [
  'AUT',
  'BEL',
  'BGR',
  'CYP'
  'CZE',
  'DEU',
  'DNK',
  'ESP',
  'EST',
  'FIN',
  'FRA',
  'GBR',
  'GRC',
  'HRV',
  'HUN',
  'IRL',
  'ITA',
  'LTU',
  'LUX',
  'LVA',
  'MLT',
  'NLD',
  'POL',
  'PRT',
  'ROU',
  'SVK',
  'SVN',
  'SWE',
]


with open(ndcs) as csvfile:
    ndcreader = csv.DictReader(csvfile)
    for row in ndcreader:
        is_eu_member = (row["Filename"].startswith("EUU_European_Union") and
                        row["ISO3"] in eu28)
        if is_eu_member:
            print("Skipping {}: EU member".format(row["Party"]))
            continue
        filename = os.path.join(pdfs_dir, row["Filename"])
        if os.path.exists(filename):
            print("Already downloaded: {}".format(row["Filename"]))
            continue
        print(row["Filename"], "<=", row["OriginalFilename"])
        url = urllib.parse.urlsplit(row["EncodedAbsUrl"])
        url = list(url)
        url[2] = urllib.parse.quote(urllib.parse.unquote(url[2]))
        url = urllib.parse.urlunsplit(url)
        urllib.request.urlretrieve(url)

        urllib.request.urlretrieve(url, filename)
