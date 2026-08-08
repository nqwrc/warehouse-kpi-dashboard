"""
Load the CSV files into a SQLite database (warehouse.db).

Run:  python build_db.py
Then explore with: sqlite3 warehouse.db  →  .tables  →  paste queries from sql/queries.sql
"""

import sqlite3
import pandas as pd

DB = "warehouse.db"

def main():
    conn = sqlite3.connect(DB)

    # create tables from the schema file
    with open("sql/schema.sql") as f:
        conn.executescript(f.read())

    # load each CSV into its table (replace = idempotent re-runs)
    for table in ["products", "lots", "order_lines"]:
        df = pd.read_csv(f"data/{table}.csv", keep_default_na=False)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"{table}: {len(df)} rows loaded")

    conn.close()
    print(f"Done → {DB}")

if __name__ == "__main__":
    main()
