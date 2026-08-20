"""Tests for the six analytical queries in sql/queries.sql, run against a
database built by the real build_db.py from the committed seeded CSVs.
Numbers are pinned to that seeded dataset (random.seed(42) in
data/generate_data.py) -- if the generator or the queries change, these
will need updating alongside them.

Run:  pytest
"""

import re

from tests.conftest import REPO_ROOT


def load_queries() -> list[str]:
    """Pull the 6 standalone SELECT statements out of sql/queries.sql.

    The count is checked here and nowhere else: a query added, removed or
    broken shifts every QUERIES[i] below, so the whole module has to stop
    at collection time rather than report six confusing failures.
    """
    text = (REPO_ROOT / "sql" / "queries.sql").read_text()
    statements = re.findall(r"SELECT.*?;", text, re.S)
    assert len(statements) == 6, f"expected 6 queries in sql/queries.sql, found {len(statements)}"
    return statements


QUERIES = load_queries()


# -------------------------------------------- Q1: overall error rate vs SLA


def test_q1_overall_error_rate(db_connection):
    row = db_connection.execute(QUERIES[0]).fetchone()
    total_lines, error_lines, error_rate_pct = row

    assert total_lines == 46247
    assert error_lines == 403
    assert error_rate_pct == 0.87  # below the 1% company target


# ------------------------------------------------ Q2: error rate per picker


def test_q2_error_rate_per_picker(db_connection):
    rows = db_connection.execute(QUERIES[1]).fetchall()
    by_picker = {picker: (lines, errors, rate) for picker, lines, errors, rate in rows}

    assert len(rows) == 8  # P01..P08
    # worst and best performer, as encoded in the generator's per-picker rates
    assert by_picker["P03"] == (5769, 115, 1.99)  # new hire, above the 1% target
    assert by_picker["P07"] == (5901, 15, 0.25)  # veteran
    # ordered worst-first
    assert rows[0][0] == "P03"


# --------------------------------------------------- Q3: weekly error trend


def test_q3_weekly_error_trend(db_connection):
    rows = db_connection.execute(QUERIES[2]).fetchall()

    assert len(rows) == 26  # WEEKS = 26 in the generator
    first_week, first_lines, first_rate = rows[0]
    assert first_week == "2026-01"
    assert first_lines == 1956
    assert first_rate == 0.77


# ---------------------------------------------------- Q4: error type Pareto


def test_q4_error_type_pareto(db_connection):
    rows = db_connection.execute(QUERIES[3]).fetchall()

    assert rows == [
        ("wrong_qty", 234),
        ("wrong_item", 95),
        ("damaged", 56),
        ("expired_lot", 18),
    ]
    assert sum(occurrences for _, occurrences in rows) == 403  # matches Q1's error_lines


# --------------------------------------------- Q5: picking volume by category


def test_q5_volume_by_category(db_connection):
    rows = db_connection.execute(QUERIES[4]).fetchall()
    by_category = {category: (lines, units) for category, lines, units in rows}

    assert len(rows) == 6  # 6 categories in the generator
    assert by_category["Vegetables"] == (8912, 58280)
    assert by_category["Meat"] == (5338, 34496)
    assert rows[0][0] == "Vegetables"  # ordered by units desc


# ---------------------------------------------------------- Q6: expiry risk


def test_q6_expiry_risk_within_30_days(db_connection):
    rows = db_connection.execute(QUERIES[5]).fetchall()

    assert len(rows) == 6
    lot_code, product_name, expiry_date, days_to_expiry, qty_received = rows[0]
    assert lot_code == "L202602-0054"
    assert product_name == "Lemon sorbet 750ml"
    assert days_to_expiry == 3
    assert all(0 <= r[3] <= 30 for r in rows)
    assert [r[3] for r in rows] == sorted(r[3] for r in rows)  # ordered by days_to_expiry
