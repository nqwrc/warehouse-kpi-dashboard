"""
Warehouse KPI Dashboard — Streamlit app.

Run from the project root:  streamlit run app/streamlit_app.py
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Warehouse KPI Dashboard", page_icon="🧊", layout="wide")

TARGET_ERROR_PCT = 1.0  # company target: stay below 1% error lines


@st.cache_data
def load_data():
    lines = pd.read_csv("data/order_lines.csv", parse_dates=["pick_date"],
                        keep_default_na=False)
    products = pd.read_csv("data/products.csv")
    lots = pd.read_csv("data/lots.csv", parse_dates=["received_date", "expiry_date"])
    lines = lines.merge(products, on="sku")
    return lines, products, lots


lines, products, lots = load_data()

# ------------------------------------------------------------- sidebar -----
st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Category", sorted(lines["category"].unique()), default=None,
    placeholder="All categories")
date_min, date_max = lines["pick_date"].min(), lines["pick_date"].max()
period = st.sidebar.date_input("Period", (date_min, date_max),
                               min_value=date_min, max_value=date_max)

view = lines.copy()
if categories:
    view = view[view["category"].isin(categories)]
if len(period) == 2:
    view = view[(view["pick_date"] >= pd.Timestamp(period[0]))
                & (view["pick_date"] <= pd.Timestamp(period[1]))]

# ------------------------------------------------------------- KPI cards ---
st.title("🧊 Warehouse KPI Dashboard")
st.caption("Synthetic dataset modeled on real refrigerated-warehouse operations "
           "(order picking with batch/expiry controls).")

is_error = view["error_type"] != ""
error_rate = 100 * is_error.mean() if len(view) else 0.0
picked_lines = len(view)
units = int(view["qty_ordered"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Picked lines", f"{picked_lines:,}")
c2.metric("Units picked", f"{units:,}")
c3.metric("Error rate", f"{error_rate:.2f}%",
          delta=f"{error_rate - TARGET_ERROR_PCT:+.2f} pp vs 1% target",
          delta_color="inverse")
c4.metric("Active pickers", view["picker_id"].nunique())

st.divider()

# ------------------------------------------------- weekly error trend ------
left, right = st.columns(2)

with left:
    st.subheader("Weekly error rate vs target")
    weekly = (view.assign(error=is_error)
                  .groupby(pd.Grouper(key="pick_date", freq="W"))["error"]
                  .agg(rate="mean", lines="count"))
    weekly["rate_pct"] = 100 * weekly["rate"]
    weekly["target"] = TARGET_ERROR_PCT
    st.line_chart(weekly[["rate_pct", "target"]],
                  color=["#e45756", "#999999"])

with right:
    st.subheader("Error rate by picker")
    by_picker = (view.assign(error=is_error)
                     .groupby("picker_id")["error"]
                     .agg(rate="mean", lines="count"))
    by_picker["rate_pct"] = (100 * by_picker["rate"]).round(2)
    st.bar_chart(by_picker["rate_pct"], color="#4c78a8")
    st.caption("Pickers above 1% are coaching candidates; the best performer "
               "can mentor.")

# ------------------------------------------------- error mix + categories --
left2, right2 = st.columns(2)

with left2:
    st.subheader("Error types (Pareto)")
    mix = (view.loc[is_error, "error_type"]
               .value_counts()
               .rename_axis("error_type")
               .to_frame("occurrences"))
    # sort="-occurrences": longest bar first, otherwise it is not a Pareto
    st.bar_chart(mix, color="#f58518", horizontal=True, sort="-occurrences")

with right2:
    st.subheader("Volume by category")
    vol = view.groupby("category")["qty_ordered"].sum()
    st.bar_chart(vol, color="#54a24b", horizontal=True, sort="-qty_ordered")

st.divider()

# ------------------------------------------------------- expiry risk -------
st.subheader("⚠️ Expiry risk (lots expiring within 30 days)")
as_of = lines["pick_date"].max()
risk = lots.copy()
risk["days_to_expiry"] = (risk["expiry_date"] - as_of).dt.days
risk = (risk[risk["days_to_expiry"].between(0, 30)]
        .merge(products, on="sku")
        .sort_values("days_to_expiry")
        .assign(expiry_date=lambda d: d["expiry_date"].dt.date)  # drop the 00:00:00
        [["lot_code", "product_name", "category", "storage_zone",
          "expiry_date", "days_to_expiry", "qty_received"]])
if risk.empty:
    st.success("No lots at expiry risk in the next 30 days.")
else:
    st.dataframe(risk, hide_index=True)
    st.caption(f"As of {as_of.date()} — FIFO discipline and promo pushes "
               "should prioritise these lots.")
