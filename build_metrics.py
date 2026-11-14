"""
Week 2: Build a table of key financial numbers for each insurer.

Reads the companyfacts.json files downloaded in Week 1 (no internet needed)
and saves:
  metrics.csv  - 3 years of revenue, net income, margin, growth, and EPS
                 for every company (open it in Excel)

Run:  python build_metrics.py
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
YEARS = 3

# Companies don't always use the same label for the same number,
# so for each metric we list the labels to try, most common first.
METRICS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"],
}


def annual_values(facts, tags):
    """Return {fiscal year: value} for full-year numbers from 10-K filings."""
    best = {}
    for tag in tags:
        item = facts["facts"].get("us-gaap", {}).get(tag)
        if not item:
            continue
        unit = "USD" if "USD" in item["units"] else next(iter(item["units"]))
        values = {}
        for row in item["units"][unit]:
            if row.get("form") != "10-K" or "start" not in row:
                continue
            # Keep only full-year periods (about 365 days), not quarters
            days = (date.fromisoformat(row["end"]) - date.fromisoformat(row["start"])).days
            if not 350 <= days <= 380:
                continue
            year = int(row["end"][:4])
            # The same year appears in several reports; keep the newest filing
            if year not in values or row["filed"] > values[year][1]:
                values[year] = (row["val"], row["filed"])
        # Use whichever label has the most recent data
        if values and (not best or max(values) > max(best)):
            best = values
    return {year: val for year, (val, _) in best.items()}


def company_rows(folder):
    facts = json.loads((folder / "companyfacts.json").read_text())
    data = {name: annual_values(facts, tags) for name, tags in METRICS.items()}
    years = sorted(data["revenue"])[-(YEARS + 1):]  # one extra year for growth
    rows = []
    for i, year in enumerate(years):
        revenue = data["revenue"].get(year)
        net_income = data["net_income"].get(year)
        prev_revenue = data["revenue"].get(years[i - 1]) if i > 0 else None
        rows.append({
            "ticker": folder.name,
            "company": facts.get("entityName", folder.name),
            "year": year,
            "revenue_billions": round(revenue / 1e9, 1) if revenue else None,
            "net_income_billions": round(net_income / 1e9, 2) if net_income is not None else None,
            "net_margin_pct": round(100 * net_income / revenue, 1) if revenue and net_income is not None else None,
            "revenue_growth_pct": round(100 * (revenue / prev_revenue - 1), 1) if revenue and prev_revenue else None,
            "eps_diluted": data["eps_diluted"].get(year),
        })
    return rows[-YEARS:]  # drop the extra year used only for growth


def main():
    folders = sorted(p for p in DATA_DIR.iterdir() if (p / "companyfacts.json").exists())
    if not folders:
        raise SystemExit(f"No data found in {DATA_DIR}. Run fetch_filings.py first.")

    table = pd.DataFrame([row for f in folders for row in company_rows(f)])
    table.to_csv(Path(__file__).parent / "metrics.csv", index=False)

    pd.set_option("display.width", 120)
    print(table.to_string(index=False))
    print("\nSaved to metrics.csv. Blank cells mean that number wasn't found; tell Claude which ones.")


if __name__ == "__main__":
    main()
