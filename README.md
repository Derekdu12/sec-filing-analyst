# SEC Filing Analyst

An AI-assisted tool that pulls SEC 10-K filings for major US health insurers, extracts key financials and risk factors, and compares the companies side by side.

**Companies:** UnitedHealth (UNH), Elevance (ELV), Cigna (CI), CVS Health/Aetna (CVS), Humana (HUM), Centene (CNC)

## How it works

1. **Data collection:** downloads each company's latest 10-K and its XBRL financial data from the SEC EDGAR API.
2. **Financial metrics:** revenue, net income, and margins come straight from SEC XBRL data, not from AI, so the numbers are exact.
3. **AI text analysis:** a large language model reads Item 1A (Risk Factors) and Item 7 (MD&A) and returns structured summaries, each linked to its source in the filing.
4. **Dashboard:** a Streamlit app to compare companies' metrics and risks side by side.

## Status

- [x] Week 1: download 10-K filings and XBRL data
- [ ] Week 2: financial metrics table
- [ ] Week 3: AI extraction of risks and outlook
- [ ] Week 4: Streamlit dashboard
- [ ] Week 5: accuracy checks
- [ ] Week 6: deployment and demo

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python fetch_filings.py
```

Downloaded data is saved to `data/` (not committed to the repo).

## Author

Derek Du, Dickinson College '28, Data Science & Quantitative Economics
