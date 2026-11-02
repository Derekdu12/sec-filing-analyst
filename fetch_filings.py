"""
Week 1: Download SEC data for a group of health insurers.

For each company this script saves:
  data/<TICKER>/10k.html           - the latest annual report (10-K)
  data/<TICKER>/filing_info.json   - date, accession number, source URL
  data/<TICKER>/companyfacts.json  - all XBRL financial numbers the company has filed

Run:  python fetch_filings.py
"""
import json
import time
from pathlib import Path

import requests

# The SEC requires a User-Agent with your name and email, or it blocks requests.
USER_AGENT = "Derek Du dume@dickinson.edu"
HEADERS = {"User-Agent": USER_AGENT}

TICKERS = ["UNH", "ELV", "CI", "CVS", "HUM", "CNC"]
DATA_DIR = Path("data")
PAUSE = 0.2  # seconds between requests; SEC allows max 10 requests/second


def get(url):
    """Download a URL politely and stop with a clear error if it fails."""
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    time.sleep(PAUSE)
    return response


def ticker_to_cik(tickers):
    """Look up each ticker's CIK (the SEC's 10-digit company ID)."""
    table = get("https://www.sec.gov/files/company_tickers.json").json()
    lookup = {row["ticker"]: str(row["cik_str"]).zfill(10) for row in table.values()}
    return {t: lookup[t] for t in tickers}


def latest_10k(cik):
    """Find the most recent 10-K in the company's filing history."""
    subs = get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
    recent = subs["filings"]["recent"]
    for form, accession, doc, date in zip(
        recent["form"], recent["accessionNumber"],
        recent["primaryDocument"], recent["filingDate"],
    ):
        if form == "10-K":
            return {"company": subs["name"], "cik": cik, "accession": accession,
                    "document": doc, "filing_date": date}
    raise ValueError(f"No 10-K found for CIK {cik}")


def filing_url(info):
    folder = info["accession"].replace("-", "")
    return (f"https://www.sec.gov/Archives/edgar/data/"
            f"{int(info['cik'])}/{folder}/{info['document']}")


def main():
    ciks = ticker_to_cik(TICKERS)

    for ticker, cik in ciks.items():
        folder = DATA_DIR / ticker
        folder.mkdir(parents=True, exist_ok=True)

        # 1. Latest 10-K (skip download if we already have it)
        info = latest_10k(cik)
        info["url"] = filing_url(info)
        tenk_path = folder / "10k.html"
        if not tenk_path.exists():
            tenk_path.write_text(get(info["url"]).text, encoding="utf-8")
        (folder / "filing_info.json").write_text(json.dumps(info, indent=2))

        # 2. XBRL financial data (the exact numbers, used in Week 2)
        facts_path = folder / "companyfacts.json"
        if not facts_path.exists():
            facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json").json()
            facts_path.write_text(json.dumps(facts))
        facts = json.loads(facts_path.read_text())
        n_tags = len(facts["facts"].get("us-gaap", {}))

        size_mb = tenk_path.stat().st_size / 1_000_000
        print(f"{ticker:4} {info['company'][:35]:35} 10-K filed {info['filing_date']}  "
              f"({size_mb:.1f} MB)  {n_tags} XBRL tags")

    print("\nDone. Everything is saved in the data/ folder.")


if __name__ == "__main__":
    main()
