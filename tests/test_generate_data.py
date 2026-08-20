"""Tests for the synthetic data generator: it must be fully reproducible
(fixed seed = 42) and it must produce the shapes the rest of the pipeline
(build_db.py, sql/queries.sql) is pinned against.

Run:  pytest
"""

import shutil
from pathlib import Path

from tests.conftest import REPO_ROOT, run_python


def generate_in(tmp_path: Path, name: str) -> Path:
    """Run the real generate_data.py in its own isolated `data/` folder."""
    run_dir = tmp_path / name
    (run_dir / "data").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "data" / "generate_data.py", run_dir / "data" / "generate_data.py")
    run_python("data/generate_data.py", cwd=run_dir)
    return run_dir / "data"


FILES = ["products.csv", "lots.csv", "order_lines.csv"]


def test_generator_output_is_byte_identical_across_runs(tmp_path):
    """random.seed(42) makes the whole generator deterministic: two runs
    must produce byte-identical CSVs, not just the same row counts."""
    data_a = generate_in(tmp_path, "run_a")
    data_b = generate_in(tmp_path, "run_b")

    for filename in FILES:
        content_a = (data_a / filename).read_bytes()
        content_b = (data_b / filename).read_bytes()
        assert content_a == content_b, f"{filename} differs between two seeded runs"


def test_generator_matches_the_committed_dataset(tmp_path):
    """The CSVs committed under data/ are exactly what the generator produces
    today -- if this drifts, the committed dataset is stale."""
    data_a = generate_in(tmp_path, "run")

    for filename in FILES:
        generated = (data_a / filename).read_bytes()
        committed = (REPO_ROOT / "data" / filename).read_bytes()
        assert generated == committed, f"committed data/{filename} is out of date"


def test_generator_produces_expected_row_counts(tmp_path):
    data_dir = generate_in(tmp_path, "run")

    def n_data_rows(filename: str) -> int:
        lines = (data_dir / filename).read_text().splitlines()
        return len(lines) - 1  # minus header

    assert n_data_rows("products.csv") == 26  # 6 categories, fixed name lists
    assert n_data_rows("lots.csv") == 109
    assert n_data_rows("order_lines.csv") == 46247


def test_generator_covers_26_weeks_starting_2026_01_05(tmp_path):
    data_dir = generate_in(tmp_path, "run")
    lines = (data_dir / "order_lines.csv").read_text().splitlines()[1:]
    pick_dates = {line.split(",")[2] for line in lines}

    assert min(pick_dates) == "2026-01-05"
    assert max(pick_dates) == "2026-07-04"  # START + 26 weeks - 2 days (last Saturday)
