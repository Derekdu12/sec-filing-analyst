# Week 1: Download SEC data for a group of health insurers.
#
# For each company, this script saves three files:
#   data/TICKER/10k.html           the latest annual report (10-K)
#   data/TICKER/filing_info.json   when it was filed and where it came from
#   data/TICKER/companyfacts.json  every financial number the company reported
#
# How to run: open this file in IDLE and press F5.

import json
import os
import time
import requests

TICKERS = ["UNH", "ELV", "CI", "CVS", "HUM", "CNC"]

# The SEC blocks requests that don't say who is asking
HEADERS = {"User-Agent": "Derek Du dume@dickinson.edu"}


def download(url):
    """Download one web address and return the response."""
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()   # stop with an error if the download failed
    time.sleep(0.2)               # short pause; the SEC allows 10 requests a second
    return response


# Step 1: The SEC identifies companies by a number called a CIK, not by ticker.
# Download the SEC's list and find the CIK for each of our tickers.
ticker_list = download("https://www.sec.gov/files/company_tickers.json").json()

ciks = {}
for entry in ticker_list.values():
    if entry["ticker"] in TICKERS:
        # CIKs are written with 10 digits, like 0000731766
        ciks[entry["ticker"]] = str(entry["cik_str"]).zfill(10)

# Step 2: For each company, find and download its latest 10-K and its numbers
for ticker in TICKERS:
    cik = ciks[ticker]
    folder = "data/" + ticker
    os.makedirs(folder, exist_ok=True)

    # Get the company's list of filings (newest first)
    history = download("https://data.sec.gov/submissions/CIK" + cik + ".json").json()
    filings = history["filings"]["recent"]

    # Go through the list until we find the first 10-K
    for i in range(len(filings["form"])):
        if filings["form"][i] == "10-K":
            accession = filings["accessionNumber"][i]
            document = filings["primaryDocument"][i]
            filing_date = filings["filingDate"][i]
            break

    # Build the web address of the report
    url = ("https://www.sec.gov/Archives/edgar/data/" + str(int(cik)) + "/"
           + accession.replace("-", "") + "/" + document)

    # Download the 10-K, unless we already have it
    report_path = folder + "/10k.html"
    if not os.path.exists(report_path):
        report = download(url).text
        file = open(report_path, "w", encoding="utf-8")
        file.write(report)
        file.close()

    # Save the details about this filing
    info = {"company": history["name"], "cik": cik, "accession": accession,
            "filing_date": filing_date, "url": url}
    file = open(folder + "/filing_info.json", "w")
    json.dump(info, file, indent=2)
    file.close()

    # Download the financial numbers, unless we already have them
    facts_path = folder + "/companyfacts.json"
    if not os.path.exists(facts_path):
        facts = download("https://data.sec.gov/api/xbrl/companyfacts/CIK" + cik + ".json").text
        file = open(facts_path, "w")
        file.write(facts)
        file.close()

    print(ticker, "-", history["name"], "- 10-K filed", filing_date)

print()
print("Done. Everything is saved in the data folder.")
