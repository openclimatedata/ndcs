import json
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
from countrynames import to_code_3
from playwright.sync_api import sync_playwright

root = Path(__file__).parents[1]
data_dir = root / "data"

languages = {
    "ar": "Arabic",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ru": "Russian",
    "zh": "Chinese",
    "pt-pt": "Portuguese",
}

url = "https://unfccc.int/NDCREG"

entries = []
nested_entries = []

BLOCK_RESOURCE_TYPES = [
    "beacon",
    "csp_report",
    "font",
    "image",
    "imageset",
    "media",
    "object",
    "texttrack",
]

BLOCK_RESOURCE_NAMES = [
    "analytics",
    "modernizer",
    "google",
    "google-analytics",
    "googletagmanager",
    "onesignal",
]


def intercept(route):
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        # print(f"Blocking `{route.request.resource_type}` resource: {route.request.url}")
        return route.abort()
    if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
        # print(f"Blocking `{route.request.url}`")
        return route.abort()
    return route.continue_()


timeout = 100_000

# Status can be 'Active' or 'Archived'
for status_field_value in ["5933", "5934"]:
    with sync_playwright() as p:
        browser = p.chromium.launch()  # Run with headless=False for debugging
        page = browser.new_page()
        page.set_default_timeout(timeout)
        page.route("**/*", intercept)
        page.goto(
            f"https://unfccc.int/NDCREG?field_party_region_target_id=All&field_document_ca_target_id=All&field_vd_status_target_id={status_field_value}&start_date_datepicker=&end_date_datepicker=&page=20"
        )
        print(page.title())

        progress = page.locator(".views-infinite-scroll-footer").inner_text()
        print(progress)

        rows = page.locator("table.table tbody tr")

        for idx in range(rows.count()):
            tds = rows.nth(idx).locator("td")
            party = tds.nth(0).inner_text().strip()
            code = "EUU" if party == "European Union (EU)" else to_code_3(party)
            try:
                version = tds.nth(4).locator("span:visible").nth(0).inner_text()
            except:
                version = ""
            status = tds.nth(5).inner_text()
            submission_date = datetime.strptime(
                tds.nth(6).inner_text(), "%d/%m/%Y"
            ).strftime("%Y-%m-%d")

            nested_entry = {
                "Code": code,
                "Party": party,
                "Version": version,
                "Status": status,
                "SubmissionDate": submission_date,
                "Ndcs": [],
                "Translations": [],
                "Addenda": [],
            }

            ndc_links = tds.nth(1).locator(
                "div.is-not-addendum.is-not-other.is-main a.is-original:visible"
            )
            for ndc_link_idx in range(ndc_links.count()):
                ndc_link = ndc_links.nth(ndc_link_idx)
                title = ndc_link.inner_text()
                lang = languages.get(ndc_link.get_attribute("hreflang"), "")
                ndc_url = ndc_link.get_attribute("href")

                entries.append(
                    {
                        "Code": code,
                        "Party": party,
                        "Title": title,
                        "FileType": "NDC",
                        "Language": lang,
                        "Version": version,
                        "Status": status,
                        "SubmissionDate": submission_date,
                        "EncodedAbsUrl": ndc_url,
                        "OriginalFilename": unquote(ndc_url.rsplit("/", 1)[1]),
                    }
                )
                nested_entry["Ndcs"].append(
                    {
                        "Title": title,
                        "FileType": "NDC",
                        "Language": lang,
                        "EncodedAbsUrl": ndc_url,
                        "OriginalFilename": unquote(ndc_url.rsplit("/", 1)[1]),
                    }
                )

            # N.B. There can be hidden links in this column, so filter for visible.
            translation_links = tds.nth(3).locator("div a.is-translation:visible")

            for translation_link_idx in range(translation_links.count()):
                translation_link = translation_links.nth(translation_link_idx)
                title = translation_link.inner_text()
                lang = languages[translation_link.get_attribute("hreflang")]
                translationUrl = translation_link.get_attribute("href")

                entries.append(
                    {
                        "Code": code,
                        "Party": party,
                        "Title": title,
                        "FileType": "Translation",
                        "Language": lang,
                        "Version": version,
                        "Status": status,
                        "SubmissionDate": submission_date,
                        "EncodedAbsUrl": translationUrl,
                        "OriginalFilename": unquote(translationUrl.rsplit("/", 1)[1]),
                    }
                )

                nested_entry["Translations"].append(
                    {
                        "Title": title,
                        "FileType": "Translation",
                        "Language": lang,
                        "EncodedAbsUrl": translationUrl,
                        "OriginalFilename": unquote(translationUrl.rsplit("/", 1)[1]),
                    }
                )

            # N.B. There can be hidden links in this column, so filter for visible.
            additional_documents_links = tds.nth(7).locator("div a.is-original:visible")
            for additional_documents_link_idx in range(
                additional_documents_links.count()
            ):
                additional_documents_link = additional_documents_links.nth(
                    additional_documents_link_idx
                )
                title = additional_documents_link.inner_text()
                lang = languages[additional_documents_link.get_attribute("hreflang")]
                additional_document_url = additional_documents_link.get_attribute(
                    "href"
                )

                entries.append(
                    {
                        "Code": code,
                        "Party": party,
                        "Title": title,
                        "FileType": "Addendum",
                        "Language": lang,
                        "Version": version,
                        "Status": status,
                        "EncodedAbsUrl": additional_document_url,
                        "OriginalFilename": unquote(
                            additional_document_url.rsplit("/", 1)[1]
                        ),
                    }
                )

                nested_entry["Addenda"].append(
                    {
                        "Title": title,
                        "FileType": "Addendum",
                        "Language": lang,
                        "EncodedAbsUrl": additional_document_url,
                        "OriginalFilename": unquote(
                            additional_document_url.rsplit("/", 1)[1]
                        ),
                    }
                )

            nested_entries.append(nested_entry)

        browser.close()

data = pd.DataFrame.from_dict(entries)
data = data.set_index("Code")
data = data.sort_values(["Party", "FileType", "Version"])
print("NDCs from {} Parties processed.".format(len(data.index.unique())))
print(
    "Status Active: {}".format(
        len(data[data.Status == "Active"].index.drop_duplicates())
    )
)
data.to_csv(str(data_dir / "ndcs.csv"))
print("Created list of NDCs in `data/ndcs.csv`")

with open(data_dir / "ndcs.json", "w") as f:
    f.write(
        json.dumps(
            sorted(
                sorted(nested_entries, key=lambda x: x["Version"], reverse=True),
                key=lambda y: y["Party"],
            ),
            indent=2,
        )
    )
print("Created JSON version of NDCs in `data/ndcs.json`")
