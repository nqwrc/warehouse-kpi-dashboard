# Warehouse KPI Dashboard 🧊

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Interactive KPI monitoring and data engineering pipeline for **refrigerated food warehouse operations**: picking accuracy tracking against a **1% error rate SLA**, operator Pareto error analysis, volume by temperature zone, and 30-day **lot expiry risk alerting**.

Modelled on real-world cold-storage logistics operations (temperature zones `-18°C` / `-25°C`, lot expiry control, FIFO prioritization, weekday peak patterns).

---

## 📈 Pipeline Architecture

```mermaid
flowchart LR
    A[Synthetic Generator\ndata/generate_data.py] -->|CSV Datasets| B[SQLite Ingestion\nbuild_db.py]
    B -->|warehouse.db| C[SQL Analytical Engine\nsql/queries.sql]
    C -->|6 KPI Queries| D[Streamlit Dashboard\napp/streamlit_app.py]
    C -->|Pandas DataFrames| E[Jupyter Notebook\nnotebooks/01_kpi_analysis.ipynb]
```

---

## 🎯 Key Operational Questions Answered

- **Error SLA Compliance**: Are picking errors maintained below the strict `< 1.0%` threshold across overall operations, weekly trends, and individual pickers?
- **Error Taxonomy Pareto**: Which root causes drive failures (wrong quantity, wrong SKU, damaged packaging, expired lot)?
- **Volume Distribution**: Volume breakdown by category, picker throughput, and temperature zone (`-18°C` frozen vs `-25°C` deep freeze).
- **Expiry Risk & FIFO Alerting**: Which lots expire within 30 days and require immediate stock rotation / clearance?

---

## 🛠️ Stack

| Layer | Technology |
|-------|------------|
| **Data Engine** | Python 3.10+ (seeded, 100% reproducible) |
| **Database** | SQLite3 schema + 6 commented analytical queries in [`sql/`](sql/) |
| **Analysis** | pandas + matplotlib narrative notebook in [`notebooks/`](notebooks/) |
| **Dashboard** | Streamlit interactive web application |

---

## 🚀 Quickstart

```bash
# 1. Clone & install dependencies
git clone https://github.com/nqwrc/warehouse-kpi-dashboard.git
cd warehouse-kpi-dashboard
pip install -r requirements.txt

# 2. Generate synthetic data & build SQLite database
python data/generate_data.py
python build_db.py

# 3. Launch Streamlit Dashboard
streamlit run app/streamlit_app.py
```

Direct SQL CLI Exploration:
```bash
sqlite3 warehouse.db < sql/queries.sql
```

> **On the foreign keys.** SQLite parses `REFERENCES` but does not enforce it unless
> `PRAGMA foreign_keys = ON` is set, and that setting lives on the connection, not in the
> file — it defaults to OFF for every new one. `build_db.py` switches it on, so the load
> is checked; if you want the same guarantee while exploring, run `PRAGMA foreign_keys = ON;`
> first in the CLI too.

---

## 📁 Repository Structure

```
├── app/
│   └── streamlit_app.py         # Streamlit interactive dashboard
├── data/
│   ├── generate_data.py         # Synthetic dataset generator (seeded)
│   └── *.csv                    # Products, lots, picking order lines
├── sql/
│   ├── schema.sql               # SQLite schema & performance indexes
│   └── queries.sql              # 6 analytical KPI queries with rationale
├── notebooks/
│   └── 01_kpi_analysis.ipynb    # Exploratory data analysis & visualizations
├── build_db.py                  # CSV ingestion into warehouse.db
└── requirements.txt             # Python dependencies
```

---

## 📝 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
