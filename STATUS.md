# status

state: active
remote: github-public
updated: 2026-09-08
stale-after-days: 30

## kpi
None. What matters here is whether the pipeline runs end to end and the analysis reads
well; neither is a number, and inventing one would only decorate this file. Declared
deviation from the 1-3 KPI rule.

## now
Pipeline, notebook and dashboard complete; the pytest suite is 22 tests and the CI
workflow is pushed. Deploy-readiness is no longer only asserted: the app was run
headless from the repo root and renders clean - no exception, four KPI tiles (46,247
picked lines, 300,739 units, 0.87% error rate, 8 pickers), four charts, the expiry
table - and narrowing the category filter reruns and drops picked lines to 5,477.
tests/test_dashboard.py pins all of that through Streamlit's AppTest harness, which
also fixes the working directory to the repo root, the same contract Streamlit
Community Cloud runs the main file under. Deploy inputs: repo nqwrc/warehouse-kpi-
dashboard, branch main, main file app/streamlit_app.py, requirements.txt at the root,
no secrets, Python 3.13 (the only version it has been run on).

Deployed and publicly reachable: https://warehouse-kpi-dashboard-6ujlbodc9l7cyxbetmzmcw.streamlit.app/
Checked from a throwaway headless-Chrome profile with no Streamlit login, which renders
the whole page - four KPI tiles, four charts, the expiry table - so an anonymous visitor
gets the dashboard and not a sign-in screen. The README links it and the repository
homepage points at it.

## backlog
- commit 8ec9357 "Added Dev Container Folder" landed on public main during the deploy
  flow: the stock Codespaces template, pinning Python 3.11 where the project is verified
  on 3.13, and running the app with `--server.enableCORS false
  --server.enableXsrfProtection false`. Dev-only, but published, and rule 1 of the
  public-repo standard is that every line holds up when asked about. Keep it aligned or
  drop it: owner's call, not taken here

## log
- 2026-09-08 - deployed on Streamlit Community Cloud and verified anonymously: headless
  Chrome over CDP with a fresh user-data-dir and no login renders the four KPI tiles
  (46,247 / 300,739 / 0.87% / 8), the four charts and the expiry table, and
  `GET /~/+/_stcore/health` returns `ok` 200 cookieless. A bare cookieless `GET /`
  returns 303 to the auth handshake for every visitor, private or not, so it measures
  nothing about access - that was the wrong check. README link and repository homepage
  set to the app URL
- 2026-08-20 (later) — dashboard screenshot added to the README (docs/dashboard.png):
  captured from the running app (headless Chrome via Selenium, Streamlit toolbar set
  to minimal, cropped to 1424x1120), shows the KPI tiles and all four charts rendered
  from the committed dataset
- 2026-08-20 — test suite and CI reviewed and repaired: the generator now writes LF, so
  the byte-equality test passes on a clean clone; CI runs pytest before the pipeline;
  build_db.py's FK pragma is covered through the loader itself; the README diagram now
  matches the code (dashboard and notebook read the CSVs) — evidence: commits c8ad338 to
  8de8dba, and `pytest -q` = 19 passed in two fresh clones (core.autocrlf input and true)
  with a fresh venv, before and after running the pipeline
- 2026-08-10 — the four commits built on 2026-08-09 pushed, and `app/` and `notebooks/`
  put under git: for two days the public repository held only the generator and the
  licence — evidence: `git ls-remote origin HEAD` was 76c329b, commit 2 of 6
- 2026-08-08 — repository created, first two commits pushed: scope, licence,
  requirements and the synthetic data generator — evidence: commits c6ad6e4, 76c329b
