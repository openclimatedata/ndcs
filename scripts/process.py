from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
from countrygroups import EUROPEAN_UNION as EU
from countrynames import to_code_3
from normality import normalize
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
}

url = "https://unfccc.int/NDCREG"


entries = []
with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.goto(url)
    print(page.title())

    page.locator('select[name="field_vd_status_target_id"]').select_option("All")

    progress = page.locator(".views-infinite-scroll-footer").inner_text()
    page.locator("text=Apply").click()
    page.wait_for_function(
        f"document.querySelector('.views-infinite-scroll-footer').innerText !== '{progress}'"
    )

    while page.locator("text=Load More").count() > 0:
        progress = page.locator(".views-infinite-scroll-footer").inner_text()
        print(progress)
        page.locator("text=Load More").click()
        page.wait_for_function(
            f"document.querySelector('.views-infinite-scroll-footer').innerText !== '{progress}'"
        )

    rows = page.query_selector_all("table.table tbody tr")
    for row in rows:
        tds = row.query_selector_all("td")
        party = tds[0].inner_text().strip()
        code = to_code_3(party)
        version = tds[4].inner_text()
        status = tds[5].inner_text()
        submission_date = datetime.strptime(tds[6].inner_text(), "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )

        if code in EU:
            code = "EUU"
        normalizedParty = normalize(
            "European-Union" if code == "EUU" else party, lowercase=False
        ).replace(" ", "-")

        title_links = tds[1].query_selector_all("div a:visible")
        for ndc_link in title_links:
            title = ndc_link.inner_text()
            lang = languages[ndc_link.get_attribute("hreflang")]
            ndc_url = ndc_link.get_attribute("href")

            normalized_filename = "{}_{}_NDC_{}_{}_{}.pdf".format(
                code, normalizedParty, version, lang, status
            )

            entries.append(
                {
                    "Code": code,
                    "Party": party,
                    "Title": title,
                    "FileType": "NDC",
                    "Language": lang,
                    "Filename": normalized_filename,
                    "Version": version,
                    "Status": status,
                    "SubmissionDate": submission_date,
                    "EncodedAbsUrl": ndc_url,
                    "OriginalFilename": unquote(ndc_url.rsplit("/", 1)[1]),
                }
            )

        # N.B. There can be hidden links in this column, so filter for visible.
        translation_links = tds[3].query_selector_all("div a:visible")
        for translation_link in translation_links:
            title = translation_link.inner_text()
            lang = languages[translation_link.get_attribute("hreflang")]
            translationUrl = translation_link.get_attribute("href")

            normalized_filename = "{}_{}_NDC_{}_Translation_{}_{}.pdf".format(
                code, normalizedParty, version, lang, status
            )

            entries.append(
                {
                    "Code": code,
                    "Party": party,
                    "Title": title,
                    "FileType": "Translation",
                    "Language": lang,
                    "Filename": normalized_filename,
                    "Version": version,
                    "Status": status,
                    "SubmissionDate": submission_date,
                    "EncodedAbsUrl": translationUrl,
                    "OriginalFilename": unquote(translationUrl.rsplit("/", 1)[1]),
                }
            )

        # N.B. There can be hidden links in this column, so filter for visible.
        addional_documents_links = tds[7].query_selector_all("div:visible a")
        for additional_documents_link in addional_documents_links:
            title = additional_documents_link.inner_text()
            lang = languages[additional_documents_link.get_attribute("hreflang")]
            additional_document_url = additional_documents_link.get_attribute("href")

            normalized_filename = "{}_{}_NDC_{}_Addendum_{}_{}_{}.pdf".format(
                code,
                normalizedParty,
                version,
                normalize(title, lowercase=False).replace(" ", "_"),
                lang,
                status,
            )

            entries.append(
                {
                    "Code": code,
                    "Party": party,
                    "Title": title,
                    "FileType": "Addendum",
                    "Language": lang,
                    "Filename": normalized_filename,
                    "Version": version,
                    "Status": status,
                    "SubmissionDate": submission_date,
                    "EncodedAbsUrl": additional_document_url,
                    "OriginalFilename": unquote(
                        additional_document_url.rsplit("/", 1)[1]
                    ),
                }
            )

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
