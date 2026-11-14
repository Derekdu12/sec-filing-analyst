# Week 2: Build a table of key financial numbers for each insurer.
#
# This script reads the companyfacts.json files that fetch_filings.py
# downloaded in Week 1, and saves one table called metrics.csv.
#
# How to run: open this file in IDLE and press F5.
# It must be in the same folder as the "data" folder.

import json
import pandas as pd

TICKERS = ["CI", "CNC", "CVS", "ELV", "HUM", "UNH"]

# Companies don't always use the same label for the same number.
# For each number we want, we list the labels to try, in order.
REVENUE_LABELS = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]
NET_INCOME_LABELS = ["NetIncomeLoss"]
EPS_LABELS = ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"]


def get_yearly_values(facts, labels):
    """Find one number (like revenue) for each year.

    Returns a dictionary like {2023: 371600000000, 2024: 400300000000}.
    """
    all_numbers = facts["facts"]["us-gaap"]

    for label in labels:
        # Skip this label if the company doesn't use it
        if label not in all_numbers:
            continue

        # The values are stored under a unit, like "USD" or "USD/shares"
        units = all_numbers[label]["units"]
        unit_name = list(units.keys())[0]

        # Put every reported value into a pandas table
        table = pd.DataFrame(units[unit_name])
        if "start" not in table.columns:
            continue

        # Keep only values from annual reports (10-K)
        table = table[table["form"] == "10-K"]
        table = table.dropna(subset=["start"])

        # Keep only full-year values (about 365 days), not quarters
        start = pd.to_datetime(table["start"])
        end = pd.to_datetime(table["end"])
        table["days"] = (end - start).dt.days
        table = table[(table["days"] >= 350) & (table["days"] <= 380)]

        # The year is the first 4 characters of the end date, like "2025-12-31"
        table["year"] = table["end"].str[:4].astype(int)

        # The same year appears in several reports. Keep the newest one.
        table = table.sort_values("filed")
        table = table.drop_duplicates(subset="year", keep="last")

        # Turn the table into a dictionary: year -> value
        values = {}
        for index, row in table.iterrows():
            values[row["year"]] = row["val"]

        # If this label gave us values, we are done
        if len(values) > 0:
            return values

    # None of the labels worked
    return {}


rows = []

for ticker in TICKERS:
    # Open the file downloaded in Week 1
    file = open("data/" + ticker + "/companyfacts.json")
    facts = json.load(file)
    file.close()

    revenue = get_yearly_values(facts, REVENUE_LABELS)
    net_income = get_yearly_values(facts, NET_INCOME_LABELS)
    eps = get_yearly_values(facts, EPS_LABELS)

    # Use the 3 most recent years
    years = sorted(revenue.keys())
    years = years[-3:]

    for year in years:
        row = {}
        row["ticker"] = ticker
        row["company"] = facts["entityName"]
        row["year"] = year

        # Revenue, in billions of dollars
        row["revenue_billions"] = round(revenue[year] / 1000000000, 1)

        # Net income (profit), and profit margin = profit / revenue
        if year in net_income:
            row["net_income_billions"] = round(net_income[year] / 1000000000, 2)
            row["net_margin_pct"] = round(net_income[year] / revenue[year] * 100, 1)

        # Revenue growth = how much bigger than last year, in percent
        last_year = year - 1
        if last_year in revenue:
            growth = (revenue[year] - revenue[last_year]) / revenue[last_year] * 100
            row["revenue_growth_pct"] = round(growth, 1)

        # Earnings per share
        if year in eps:
            row["eps_diluted"] = eps[year]

        rows.append(row)

# Turn the list of rows into a table, save it, and show it
columns = ["ticker", "company", "year", "revenue_billions", "net_income_billions",
           "net_margin_pct", "revenue_growth_pct", "eps_diluted"]
table = pd.DataFrame(rows, columns=columns)
table.to_csv("metrics.csv", index=False)

pd.set_option("display.width", 150)
print(table.to_string(index=False))
print()
print("Saved to metrics.csv")
