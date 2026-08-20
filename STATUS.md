# status

state: active
remote: github-public
updated: 2026-08-20
stale-after-days: 30

## kpi
None. What matters here is whether the pipeline runs end to end and the analysis reads
well; neither is a number, and inventing one would only decorate this file. Declared
deviation from the 1-3 KPI rule.

## now
Pipeline, notebook and dashboard complete; a 19-test pytest suite, a CI workflow and the
README corrections sit on local `main`, seven commits past `origin/main` (675a5ae).
Deploy-readiness is confirmed: the dashboard reads the committed CSVs, no build step.

## backlog
- push the local commits (675a5ae..HEAD) to the public remote — owner action
- deploy the dashboard on Streamlit Community Cloud, then set the repository homepage
- add a dashboard screenshot to the README

## log
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
