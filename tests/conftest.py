"""Shared fixtures.

Neither generate_data.py nor build_db.py exposes an importable function --
both are top-level scripts that read/write relative paths (data/*.csv,
sql/schema.sql, warehouse.db). Tests therefore run them as subprocesses
inside isolated tmp_path directories, copying in only the inputs each
script needs, so a test run never touches the real data/*.csv or
warehouse.db in the repo working tree.
"""

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_python(script: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run `python <script>` with cwd set, raising on a non-zero exit."""
    result = subprocess.run(
        [sys.executable, script],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{script} failed (exit {result.returncode})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


@pytest.fixture
def built_db(tmp_path: Path) -> Path:
    """A warehouse.db built by the real build_db.py from the real seeded CSVs.

    Copies build_db.py, sql/schema.sql and the three committed data/*.csv
    files into an isolated tmp_path, runs build_db.py there, and returns
    the path to the resulting warehouse.db.
    """
    (tmp_path / "sql").mkdir()
    (tmp_path / "data").mkdir()
    shutil.copy(REPO_ROOT / "build_db.py", tmp_path / "build_db.py")
    shutil.copy(REPO_ROOT / "sql" / "schema.sql", tmp_path / "sql" / "schema.sql")
    for name in ("products.csv", "lots.csv", "order_lines.csv"):
        shutil.copy(REPO_ROOT / "data" / name, tmp_path / "data" / name)

    run_python("build_db.py", cwd=tmp_path)

    db_path = tmp_path / "warehouse.db"
    assert db_path.exists(), "build_db.py did not create warehouse.db"
    return db_path


@pytest.fixture
def db_connection(built_db: Path) -> sqlite3.Connection:
    """A connection to `built_db` with foreign keys enforced, matching build_db.py."""
    conn = sqlite3.connect(built_db)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()
