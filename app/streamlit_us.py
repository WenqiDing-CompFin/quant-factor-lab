"""US equities factor lab dashboard — MFE portfolio visualization."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantlab.backtest import performance_stats, run_long_only_backtest
from quantlab.data.loader import load_config, load_panel
from quantlab.factors import FACTOR_CATALOG, compute_factors, list_factors
from quantlab.portfolio import combine_factors
from quantlab.research import (
    factor_corr_matrix,
    factor_ic_series,
    layer_returns,
    summarize_ic,
)

st.set_page_config(page_title="Quant Factor Lab · US", layout="wide")
st.title("Quant Factor Lab — US Equities")
st.caption(
    "Cross-sectional factor research · selection → IC/ICIR → layers → multi-factor → NAV"
)


@st.cache_data(show_spinner="Loading US panel…")
def get_panel():
    return load_panel(ROOT / "configs" / "us_demo.yaml", source="synthetic")


cfg = load_config(ROOT / "configs" / "us_demo.yaml")
panel = get_panel()

with st.sidebar:
    st.header("Factor selection")
    st.markdown("Start from an **economic story**, then inspect IC / layers.")
    categories = sorted({s.category for s in list_factors()})
    cat = st.multiselect("Category", categories, default=categories)
    candidates = [s.name for s in list_factors() if s.category in cat]
    selected = st.multiselect(
        "Factors",
        candidates,
        default=[f for f in cfg["factors"] if f in candidates][:5],
    )
    top_q = st.slider("Top quantile (long-only)", 0.1, 0.4, float(cfg["top_quantile"]), 0.05)
    cost = st.slider("Cost (bps)", 0, 30, int(cfg["transaction_cost_bps"]), 1)
    run = st.button("Run research", type="primary")

if not selected:
    st.info("Select at least one factor in the sidebar.")
    st.stop()

st.subheader("1. Factor stories")
cols = st.columns(min(3, len(selected)))
for i, name in enumerate(selected):
    spec = FACTOR_CATALOG[name]
    with cols[i % len(cols)]:
        st.markdown(f"**{name}** · `{spec.category}`")
        st.write(spec.description_en)
        st.caption(spec.why_it_might_work)

if not run and "us_fdf" not in st.session_state:
    st.warning("Click **Run research** after choosing factors.")
    st.stop()

if run:
    st.session_state["us_fdf"] = compute_factors(panel, factor_names=selected)
    st.session_state["us_selected"] = selected
    st.session_state["us_top_q"] = top_q
    st.session_state["us_cost"] = cost

fdf = st.session_state["us_fdf"]
selected = st.session_state["us_selected"]
top_q = st.session_state["us_top_q"]
cost = st.session_state["us_cost"]

st.subheader("2. Rank IC")
ic_rows = []
ic_map = {}
for name in selected:
    ic = factor_ic_series(fdf, name)
    ic_map[name] = ic
    s = summarize_ic(ic)
    s["factor"] = name
    ic_rows.append(s)
ic_table = pd.DataFrame(ic_rows).set_index("factor")[
    ["mean_ic", "icir", "t_stat", "pos_ratio", "n"]
]
st.dataframe(
    ic_table.style.format(
        {"mean_ic": "{:+.4f}", "icir": "{:+.3f}", "t_stat": "{:+.2f}", "pos_ratio": "{:.1%}"}
    ),
    use_container_width=True,
)
fig_ic = px.line(pd.DataFrame(ic_map), title="Rank IC over time")
fig_ic.add_hline(y=0, line_dash="dot")
st.plotly_chart(fig_ic, use_container_width=True)

best = ic_table["icir"].idxmax()
c1, c2 = st.columns(2)
with c1:
    st.subheader(f"3. Quantile layers · `{best}`")
    layered = layer_returns(fdf, best, n_layers=5)
    fig_layer = px.bar(
        layered.mean().drop(labels=["long_short"], errors="ignore"),
        title="Mean forward return by quantile",
    )
    st.plotly_chart(fig_layer, use_container_width=True)
with c2:
    st.subheader("4. Factor correlation")
    corr = factor_corr_matrix(fdf, selected)
    fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", title="Avg Spearman corr")
    st.plotly_chart(fig_corr, use_container_width=True)

st.subheader("5. Multi-factor NAV")
combo = combine_factors(fdf, selected)
bt = run_long_only_backtest(combo, "score_combo", top_quantile=top_q, cost_bps=cost)
stats = performance_stats(bt)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ann. return", f"{stats['ann_return']:.2%}")
m2.metric("Sharpe", f"{stats['sharpe']:.2f}")
m3.metric("Max DD", f"{stats['max_drawdown']:.2%}")
m4.metric("Avg turnover", f"{stats['avg_turnover']:.1%}")

fig_nav = go.Figure()
fig_nav.add_trace(go.Scatter(x=bt.index, y=bt["nav"], name="Composite NAV", mode="lines"))
fig_nav.update_layout(title="Long-only top-quantile NAV (net of cost)", yaxis_title="NAV")
st.plotly_chart(fig_nav, use_container_width=True)

st.markdown(
    """
---
**How to present this (MFE admissions)**
1. Economic rationale first, IC/ICIR second, returns last.
2. Correlation heatmap shows you did not blindly stack redundant factors.
3. Always report costs and turnover; paper alpha without frictions is not research.
4. This demo uses a **reproducible synthetic US panel** to validate the pipeline;
   swap `src/quantlab/data/` for CRSP/Compustat or Yahoo/Polygon later.
"""
)
