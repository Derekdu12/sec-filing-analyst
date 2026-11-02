# SEC Filing Analyst

A tool that reads the yearly reports of big US health insurance companies and shows how they compare, using AI to do the slow reading.

## What problem does it solve?

Every public company has to publish a yearly report called a **10-K**. These reports are often 200+ pages long. Comparing six companies by hand can take days.

This tool downloads the reports automatically, pulls out the important numbers, and uses AI to summarize the biggest risks. The goal is to understand six companies in minutes instead of days.

## Which companies?

| Ticker | Company |
|---|---|
| UNH | UnitedHealth Group |
| ELV | Elevance Health |
| CI | Cigna |
| CVS | CVS Health (Aetna) |
| HUM | Humana |
| CNC | Centene |

## How it works

1. **Download the reports.** The tool gets each company's latest 10-K from the SEC's free website.
2. **Get the numbers.** Revenue, profit, and growth come straight from the SEC's official data, not from AI, so they are exact.
3. **Summarize the text with AI.** AI reads the "Risk Factors" and "Management's Discussion" sections and lists the key points, with a link back to where each point came from.
4. **Show it on one page.** A simple website lets you pick companies and compare them side by side.

## Progress

- [x] Week 1: Download the reports and financial data
- [ ] Week 2: Build a table of key numbers
- [ ] Week 3: Use AI to summarize risks
- [ ] Week 4: Build the comparison website
- [ ] Week 5: Check the AI's answers for accuracy
- [ ] Week 6: Publish the website and record a demo

## How to run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python fetch_filings.py
```

The downloaded reports are saved in a `data` folder on your computer. They are not uploaded here because they are large and free to download from the SEC.

## About me

Derek Du, Dickinson College, Class of 2028. Data Science & Quantitative Economics.
