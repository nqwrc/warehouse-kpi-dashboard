"""Tests for sql/schema.sql and build_db.py: the foreign-key enforcement
claim in the README ("primary and foreign keys enforced at load time,
verified by rejection") and the row counts the loader must produce from
the committed seeded CSVs.

Run:  pytest
"""

import sqlite3

from tests.conftest import REPO_ROOT

BAD_ORDER_LINE = (
    "INSERT INTO order_lines "
    "(line_id, order_id, pick_date, picker_id, sku, lot_code, qty_ordered, error_type) "
    "VALUES (999999, 1, '2026-01-01', 'PX', 'NO-SUCH-SKU', 'NO-SUCH-LOT', 1, '')"
)


def fresh_schema_connection() -> sqlite3.Connection:
    """An in-memory database built straight from the real sql/schema.sql."""
    conn = sqlite3.connect(":memory:")
    conn.executescript((REPO_ROOT / "sql" / "schema.sql").read_text())
    return conn


# ------------------------------------------------------- PRAGMA behaviour --


def test_foreign_keys_are_off_by_default_on_a_new_connection():
    """The premise the README warning rests on: SQLite does not enforce
    REFERENCES unless PRAGMA foreign_keys is switched on for that connection."""
    conn = fresh_schema_connection()

    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 0


def test_bad_foreign_key_is_silently_accepted_when_pragma_is_off():
    """Without the PRAGMA, a line referencing a non-existent sku/lot inserts
    without error -- the failure mode build_db.py exists to close off."""
    conn = fresh_schema_connection()

    conn.execute(BAD_ORDER_LINE)  # must not raise
    count = conn.execute(
        "SELECT COUNT(*) FROM order_lines WHERE line_id = 999999"
    ).fetchone()[0]
    assert count == 1


def test_bad_foreign_key_is_rejected_when_pragma_is_on():
    """This is the exact statement build_db.py runs before loading data."""
    conn = fresh_schema_connection()
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        conn.execute(BAD_ORDER_LINE)
    except sqlite3.IntegrityError as exc:
        assert "FOREIGN KEY constraint failed" in str(exc)
    else:
        raise AssertionError("expected sqlite3.IntegrityError, insert succeeded")


def test_duplicate_primary_key_is_rejected():
    conn = fresh_schema_connection()
    conn.execute(
        "INSERT INTO products (sku, product_name, category, storage_zone) "
        "VALUES ('SKU1000', 'Peas 450g', 'Vegetables', '-18C')"
    )
    try:
        conn.execute(
            "INSERT INTO products (sku, product_name, category, storage_zone) "
            "VALUES ('SKU1000', 'Duplicate', 'Vegetables', '-18C')"
        )
    except sqlite3.IntegrityError as exc:
        assert "UNIQUE constraint failed" in str(exc)
    else:
        raise AssertionError("expected sqlite3.IntegrityError, duplicate PK accepted")


# ------------------------------------------------------------- build_db.py --


def test_build_db_loads_the_expected_row_counts(db_connection):
    """Pinned against the committed, seeded data/*.csv files."""
    counts = {
        table: db_connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("products", "lots", "order_lines")
    }
    assert counts == {"products": 26, "lots": 109, "order_lines": 46247}


def test_build_db_preserves_the_declared_foreign_keys(db_connection):
    """Regression test for the bug fixed in 8103181: a loader that recreates
    tables with to_sql(if_exists="replace") lets pandas infer the schema
    from the dataframe, silently dropping every constraint sql/schema.sql
    declared. PRAGMA foreign_key_list must still show them after a real
    build_db.py run."""
    lots_fks = db_connection.execute("PRAGMA foreign_key_list(lots)").fetchall()
    order_lines_fks = db_connection.execute("PRAGMA foreign_key_list(order_lines)").fetchall()

    assert len(lots_fks) == 1
    assert len(order_lines_fks) == 2


def test_build_db_preserves_the_primary_keys(db_connection):
    def pk_columns(table: str) -> list[str]:
        return [row[1] for row in db_connection.execute(f"PRAGMA table_info({table})") if row[5]]

    assert pk_columns("products") == ["sku"]
    assert pk_columns("lots") == ["lot_code"]
    assert pk_columns("order_lines") == ["line_id"]


def test_build_db_rejects_a_bad_foreign_key_after_loading(db_connection):
    """End-to-end version of test_bad_foreign_key_is_rejected_when_pragma_is_on,
    against the real loaded database rather than a bare schema."""
    try:
        db_connection.execute(BAD_ORDER_LINE)
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("expected sqlite3.IntegrityError, insert succeeded")
