# status

state: active
remote: github-public
updated: 2026-08-10
stale-after-days: 30

## kpi
None. What matters here is whether the pipeline runs end to end and the analysis reads
well; neither is a number, and inventing one would only decorate this file. Declared
deviation from the 1-3 KPI rule.

## now
Complete and public: synthetic data generator, dataset, SQLite schema and loader, six KPI
queries, the analysis notebook and the Streamlit dashboard, all on `main` and in sync with
the remote. The dashboard is not deployed anywhere yet, so the repository has no homepage.

## backlog
- deploy the dashboard on Streamlit Community Cloud, then set the repository homepage
- add a dashboard screenshot to the README

## log
- 2026-08-10 — the four commits built on 2026-08-09 pushed, and `app/` and `notebooks/`
  put under git: for two days the public repository held only the generator and the
  licence — evidence: `git ls-remote origin HEAD` was 76c329b, commit 2 of 6
- 2026-08-08 — repository created, first two commits pushed: scope, licence,
  requirements and the synthetic data generator — evidence: commits c6ad6e4, 76c329b
