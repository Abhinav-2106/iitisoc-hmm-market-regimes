# Project Pipeline

## Pipeline

Market Data
→ Feature Engineering
→ HMM Training
→ State Detection
→ Regime Analysis
→ Trading Strategy
→ Dashboard

---

## Data Output

File: clean_data.csv

Columns:
- Date
- Open
- High
- Low
- Close
- Volume

---

## Feature Output

File: features.csv

Columns:
- Date
- returns
- volatility

Owner: Abhinav + Samarth

---

## HMM Output

File: states.csv

Columns:
- Date
- state

Owner: Abhinav + Samarth



## Regime Analysis Output

File: regime_labels.csv

Columns:
- State
- Label

Owner: Aditya


## Strategy Output

File: signals.csv

Columns:
- Date
- Signal

Owner: Shubham
