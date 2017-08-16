import os
import re
import urllib.request

import pandas as pd

from countrygroups import EUROPEAN_UNION as eu28
from normality import normalize
from pathlib import Path

root = Path(__file__).parents[1]
data_dir = root / "data"

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


# Mexico's NDC is actually in English.
data = data.set_value(
    data[data["ISO3"] == "MEX"].index[0], "Language", "English")


def set_file_type(row):

    # Panama's Cover letter is classified as "NDC", set to "Addendum":
    if row["Title"] == "Panama NDC Cover Letter":
        filetype = "Addendum"
    elif "Archived" in row["Title"]:
        filetype = "Archived"
    else:
        filetype = row["FileType"]
    return filetype

data["FileType"] = data.apply(set_file_type, axis=1)


def create_filename(row):
    file_type = row["FileType"]
    if file_type == "Translation":
        file_type = "NDC_Translation"
    elif file_type == "Addendum":
        file_type = "NDC_Addendum"
    name = "{}_{}".format(row["Number"], file_type)

    if "revised" in row["Title"].lower():
        name += "_Revised"
    elif "archived" in row["Title"].lower():
        name = "{}_NDC_Archived".format(row["Number"])

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
        party = "European-Union"
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
data.to_csv(str(data_dir / "ndcs.csv"))
print("Created list of NDCs in `data/ndcs.csv`")
