"""Smoke test for the Streamlit dashboard, run headless through Streamlit's
own AppTest harness -- no browser, no server, no screenshot.

The other three modules cover the pipeline that produces the CSVs. Nothing
covered app/streamlit_app.py, so a change that broke the page would have
surfaced only in the deployed app, in front of whoever followed the link.
This runs the script end to end, asserts it raises nothing, and then moves a
filter: a dashboard that renders once and dies on the first interaction is
exactly the failure a screenshot cannot catch.

The app reads data/*.csv by relative path, so it is correct only when the
working directory is the repo root. That is also how Streamlit Community
Cloud runs it -- it clones the repo and runs the main file path from the
root -- so fixing the directory here keeps the test and the deployment on
the same contract. Read-only throughout: the app opens the committed CSVs
and writes nothing.
"""

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import REPO_ROOT

APP = REPO_ROOT / "app" / "streamlit_app.py"

# st.line_chart and st.bar_chart both render as Vega-Lite specs, so the four
# charts are one element type rather than two.
CHART = "vega_lite_chart"


def picked_lines(app: AppTest) -> int:
    """The first KPI tile as a number. It is displayed thousands-separated."""
    return int(app.metric[0].value.replace(",", ""))


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    monkeypatch.chdir(REPO_ROOT)
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    return at


def test_the_page_renders_without_raising(app: AppTest) -> None:
    assert not app.exception, app.exception
    assert not app.error, app.error


def test_every_tile_chart_and_table_is_on_the_page(app: AppTest) -> None:
    """Pinned to the page as designed, so a silently dropped panel fails here.

    Labels rather than a count: a rename is a change to what the page claims
    it is measuring, which is worth failing on.
    """
    assert [tile.label for tile in app.metric] == [
        "Picked lines",
        "Units picked",
        "Error rate",
        "Active pickers",
    ]
    assert len(app.get(CHART)) == 4
    assert len(app.dataframe) == 1


def test_narrowing_the_category_filter_reruns_and_shrinks_the_totals(
    app: AppTest,
) -> None:
    """The reactive half of the app, which the render test cannot reach.

    Streamlit reruns the whole script on a widget change, so this asserts
    both that the rerun survives and that it actually filtered: one of the
    six categories has to pick fewer lines than all six.
    """
    everything = picked_lines(app)
    categories = app.multiselect[0].options
    assert len(categories) > 1, "the filter needs something to narrow from"

    filtered = app.multiselect[0].set_value(categories[:1]).run()

    assert not filtered.exception, filtered.exception
    assert picked_lines(filtered) < everything
