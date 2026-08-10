"""
Load the CSV files into a SQLite database (warehouse.db).

Run:  python build_db.py
Then explore with: sqlite3 warehouse.db  ->  .tables  ->  paste queries from sql/queries.sql
"""

import sqlite3
import pandas as pd

DB = "warehouse.db"

# Parents first: lots references products, and order_lines references both.
# Inserts follow this order, drops follow the reverse.
TABLES = ["products", "lots", "order_lines"]


def main():
    conn = sqlite3.connect(DB)

    # SQLite parses REFERENCES but does not enforce it unless this is switched on,
    # and it is per connection, not stored in the file. Without it the foreign keys
    # in sql/schema.sql are documentation, not constraints.
    conn.execute("PRAGMA foreign_keys = ON")

    # Drop before creating, children first so the foreign keys do not block it.
    # This also rebuilds a database left behind by an older version of this script,
    # which loaded with to_sql(if_exists="replace") -- that drops the table and lets
    # pandas recreate it from the dataframe dtypes, silently discarding every primary
    # key, foreign key and index declared in the schema.
    for table in reversed(TABLES):
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    with open("sql/schema.sql") as f:
        conn.executescript(f.read())

    # Append into the tables the schema just created; never replace them.
    for table in TABLES:
        df = pd.read_csv(f"data/{table}.csv", keep_default_na=False)
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"{table}: {len(df)} rows loaded")

    conn.commit()
    conn.close()
    print(f"Done -> {DB}")


if __name__ == "__main__":
    main()
