# Warehouse KPI Dashboard 🧊

KPI monitoring for a **refrigerated food warehouse**: picking accuracy, error
analysis by operator, volume by category and lot **expiry-risk** tracking.

I spent a season picking orders in a refrigerated warehouse with strict
batch/expiry controls and a hard target — keep the picking error rate **below
1%**. This project rebuilds that monitoring as a proper data product: the
dataset is **synthetic but modeled on the real operation** (temperature zones,
lot codes, error taxonomy, weekday volume patterns).

<!-- TODO: add a dashboard screenshot here
![Dashboard](docs/screenshot.png) -->

## What it answers

- Are we below the 1% error-rate target — overall, weekly, per picker?
- Which error types dominate (wrong quantity, wrong item, damaged, expired lot)?
- Where does picking volume actually go, by category and temperature zone?
- Which lots expire within 30 days and need FIFO priority?

## Stack

| Layer | Tool |
|-------|------|
| Data generation | Python (seeded, reproducible) |
| Storage & queries | SQLite — schema + 6 commented KPI queries in [`sql/`](sql/) |
| Analysis | pandas + matplotlib notebook in [`notebooks/`](notebooks/) |
| Dashboard | Streamlit |

## Run it

```bash
pip install -r requirements.txt

python data/generate_data.py      # 1. generate the synthetic CSVs
python build_db.py                # 2. load them into SQLite (warehouse.db)
streamlit run app/streamlit_app.py  # 3. open the dashboard
```

Explore the SQL directly:

```bash
sqlite3 warehouse.db < sql/queries.sql
```

## Project structure

```
├── data/
│   ├── generate_data.py   # synthetic data generator (seeded)
│   └── *.csv              # products, lots, order_lines
├── sql/
│   ├── schema.sql         # tables + indexes
│   └── queries.sql        # 6 KPI queries, one operational question each
├── notebooks/
│   └── 01_kpi_analysis.ipynb  # narrative analysis with charts
├── app/
│   └── streamlit_app.py   # interactive dashboard
└── build_db.py            # CSV → SQLite loader
```

## KPI definitions

- **Error rate** = lines with an error / total picked lines (target < 1%)
- **Expiry risk** = lots with 0–30 days to expiry as of the last activity date
- **Volume** = units picked, grouped by category / week / picker

## Notes

- Data is 100% synthetic — no employer data was used. Patterns (error
  taxonomy, -18°C/-25°C zones, Mon–Tue volume peaks, one struggling new hire)
  reflect first-hand operational experience.
- License: MIT
