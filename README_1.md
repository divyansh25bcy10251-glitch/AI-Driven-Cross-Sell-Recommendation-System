# Bank Cross-Sell Intelligence Dashboard
**VITB AI Innovators Hub · Data Analyst Track Screening Task**

## Setup

```bash
pip install streamlit pandas numpy plotly matplotlib seaborn
```

Place `bank-full.csv` (UCI Bank Marketing Dataset, semicolon-separated) in the same folder.

## Run

```bash
# EDA script (outputs 4 PNG charts + terminal summary)
python eda.py

# Interactive dashboard
streamlit run app.py
```

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard with interactive filters |
| `eda.py` | Standalone EDA script (reproduces all findings) |
| `EXPLANATION.md` | Understanding of dataset, methods, and findings |
| `bank-full.csv` | UCI Bank Marketing Dataset (not included — download separately) |

## Download dataset
https://archive.ics.uci.edu/dataset/222/bank+marketing → use `bank-full.csv`
