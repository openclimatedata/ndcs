import os
import re
import urllib.request

import pandas as pd

from normality import normalize

path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(path, "../data/")

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

url = "http://www4.unfccc.int/ndcregistry/Pages/All.aspx"
regex = re.compile('\[\{"Title.+?INDC.+?\}\]')

with urllib.request.urlopen(url) as response:
    html = response.read()

data = regex.findall(html.decode("UTF-8"))[0]

data = pd.read_json(data)
data.columns = [c.replace("NDC", "") for c in data.columns]

data = data.rename(columns={
    "OnBehalfOf": "Party",
    "Name": "OriginalFilename"
})

data["SubmissionDate"] = pd.to_datetime(data["SubmissionDate"])

# Panama's Cover letter is classified as "NDC", set to "Addendum"
data.set_value(data[data.Title == "Panama NDC Cover Letter"].index,
    "FileType", "Addendum")


def create_filename(row):
    name = "{}_{}".format(row["Number"], row["FileType"])

    if "revised" in row["Title"].lower():
        name += "_Revised"
    elif "archived" in row["Title"].lower():
        name += "_Archived"

    # Special casing PNG with multiple Addendums
    if row["Party"] == "Papua New Guinea":
        if "letter" in row["Title"]:
            name += "_Satisfactory_Letter"
        elif "Explanatory Note" in row["Title"]:
            name += "_Explanatory_Note"
        elif "PA Implementation Act" in row["Title"]:
            name += "_PA_Implementation_Act"
        elif "Management Act" in row["Title"]:
            name += "_Climate_Change_Management_Act"

    code = row["ISO3"]
    party = normalize(row["Party"], lowercase=False).replace(" ", "-")
    if row["OriginalFilename"].startswith("LV-03-06-EU") and code in eu28:
        code = "EUU"
        party = "European_Union"
    name = "{}_{}_{}_{}.pdf".format(
        code,
        party,
        name,
        row["Language"])
    return name


data["Filename"] = data.apply(create_filename, axis=1)

data = data.set_index("ISO3")
data = data[[
    "Party",
    "Title",
    "FileType",
    "Language",
    "Filename",
    "Number",
    "SubmissionDate",
    "EncodedAbsUrl",
    "OriginalFilename"
]]

data = data.sort_values(["Party", "FileType"])

print("NDCs from {} Parties processed.".format(len(data.index.unique())))
data.to_csv(os.path.join(data_dir, "ndcs.csv"))
print("Created list of NDCs in `data/ndcs.csv`")

