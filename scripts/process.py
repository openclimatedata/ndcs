import json
import re
import urllib.request

import pandas as pd

from countrygroups import EUROPEAN_UNION as EU
from normality import normalize
from pathlib import Path

root = Path(__file__).parents[1]
data_dir = root / "data"

url = "https://www4.unfccc.int/sites/NDCStaging/Pages/All.aspx"
regex = re.compile('\[\{.+?NDCNumber.+?\}\]')

with urllib.request.urlopen(url) as response:
    html = response.read()

data = regex.findall(html.decode("UTF-8"))[0]

data = pd.DataFrame.from_dict(json.loads(data))
data.columns = [c.replace("NDC", "") for c in data.columns]

data = data.rename(columns={
    "ISO3": "Code",
    "OnBehalfOf": "Party",
    "Name": "OriginalFilename"
})

data["Party"] = data["Party"].apply(str.strip)


data["SubmissionDate"] = pd.to_datetime(
    data["SubmissionDate"].apply(lambda x: x.split(" ")[0]), format="%d/%m/%Y")


def set_file_type(row):

    # Panama's Cover letter is classified as "NDC", set to "Addendum":
    if row["Title"] == "Panama NDC Cover Letter":
        filetype = "Addendum"
    # Special case SLV with Revised NDC
    elif ((row["Party"] == "El Salvador") and
        ("revised" not in row["Title"].lower())):
        filetype = "Archived"
    # Special case RWA with Updated NDC
    elif (row["Party"] == "Rwanda") and (row["Title"] == "Rwanda First NDC"):
        filetype = "Archived"
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

    # Special case PSE with multiple Addendums
    if row["Party"] == "State of Palestine":
        if "SPM" in row["OriginalFilename"]:
            name += "_Summary_Policy_Makers"
        elif "Cobenefits" in row["Title"]:
            name += "_Cobenefits"
        elif "Implementation" in row["Title"]:
            name += "_Implementation_Road_Map"
        elif "Approval" in row["Title"]:
            name += "_Approval"

    # Special case PNG with multiple Addendums
    if row["Party"] == "Papua New Guinea":
        if "letter" in row["Title"]:
            name += "_Satisfactory_Letter"
        elif "Explanatory Note" in row["Title"]:
            name += "_Explanatory_Note"
        elif "PA Implementation Act" in row["Title"]:
            name += "_PA_Implementation_Act"
        elif "Management Act" in row["Title"]:
            name += "_Climate_Change_Management_Act"

    code = row["Code"]
    party = normalize(row["Party"], lowercase=False).replace(" ", "-")
    if code in EU:
        code = "EUU"
        party = "European-Union"
    name = "{}_{}_{}_{}.pdf".format(
        code,
        party,
        name,
        row["Language"])
    return name

data["Filename"] = data.apply(create_filename, axis=1)

data = data.set_index("Code")

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

print("First NDCs: {}".format(
    len(data[data.Number == "First"].index.drop_duplicates())
))
print("Second NDCs: {}".format(
    len(data[data.Number == "Second"].index.drop_duplicates())
))
data.to_csv(str(data_dir / "ndcs.csv"))
print("Created list of NDCs in `data/ndcs.csv`")
