"""Interactive A-share factor lab dashboard (portfolio / admissions demo)."""

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
from quantlab.research import factor_ic_series, layer_returns, summarize_ic

st.set_page_config(page_title="Quant Factor Lab · A-share", layout="wide")
st.title("Quant Factor Lab")
st.caption("A-share factor research bench · see also `streamlit run app/streamlit_us.py`")


@st.cache_data(show_spinner="Loading panel…")
def get_panel():
    return load_panel(ROOT / "configs" / "ashare_demo.yaml", source="synthetic")


cfg = load_config(ROOT / "configs" / "ashare_demo.yaml")
panel = get_panel()

with st.sidebar:
    st.header("Factor selection")
    st.markdown("先选**有经济含义**的因子，再看 IC / 分层。")
    categories = sorted({s.category for s in list_factors()})
    cat = st.multiselect("Category", categories, default=categories)
    candidates = [s.name for s in list_factors() if s.category in cat]
    selected = st.multiselect(
        "Factors",
        candidates,
        default=[f for f in cfg["factors"] if f in candidates][:5],
    )
    top_q = st.slider("Top quantile (long-only)", 0.1, 0.4, float(cfg["top_quantile"]), 0.05)
    cost = st.slider("Cost (bps, one-way proxy)", 0, 50, int(cfg["transaction_cost_bps"]), 5)
    run = st.button("Run research", type="primary")

if not selected:
    st.info("← 在左侧至少选择一个因子。从价值 / 动量 / 质量开始最合适。")
    st.stop()

# Factor stories
st.subheader("1. 因子故事（选取的起点）")
story_cols = st.columns(min(3, len(selected)))
for i, name in enumerate(selected):
    spec = FACTOR_CATALOG[name]
    with story_cols[i % len(story_cols)]:
        st.markdown(f"**{name}** · `{spec.category}`")
        st.write(spec.description_zh)
        st.caption(f"为何可能有效：{spec.why_it_might_work}")
        st.caption(f"常见坑：{spec.common_pitfalls}")

if not run and "fdf" not in st.session_state:
    st.warning("配置好看后点左侧 **Run research**。")
    st.stop()

if run:
    st.session_state["fdf"] = compute_factors(panel, factor_names=selected)
    st.session_state["selected"] = selected
    st.session_state["top_q"] = top_q
    st.session_state["cost"] = cost

fdf = st.session_state["fdf"]
selected = st.session_state["selected"]
top_q = st.session_state["top_q"]
cost = st.session_state["cost"]

# IC table
st.subheader("2. 单因子 Rank IC")
ic_rows = []
ic_series_map = {}
for name in selected:
    ic = factor_ic_series(fdf, name)
    ic_series_map[name] = ic
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

ic_df = pd.DataFrame(ic_series_map)
fig_ic = px.line(ic_df, title="Rank IC over time", labels={"value": "IC", "variable": "factor"})
fig_ic.add_hline(y=0, line_dash="dot")
st.plotly_chart(fig_ic, use_container_width=True)

# Layers + backtest for best ICIR
best = ic_table["icir"].idxmax()
st.subheader(f"3. 分层收益 · 最佳单因子 `{best}`")
layered = layer_returns(fdf, best, n_layers=5)
fig_layer = px.bar(
    layered.mean().drop(labels=["long_short"], errors="ignore"),
    title="Mean forward return by quantile (Q5 should > Q1)",
    labels={"value": "mean ret", "index": "layer"},
)
st.plotly_chart(fig_layer, use_container_width=True)

st.subheader("4. 多因子合成 + 净值")
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
fig_nav.update_layout(title="Long-only top-quantile NAV (net of cost proxy)", yaxis_title="NAV")
st.plotly_chart(fig_nav, use_container_width=True)

st.markdown(
    """
---
**怎么读这些图（申请材料口述稿）**
1. 先讲因子的经济逻辑，再展示 IC / ICIR，而不是先晒收益率。
2. 分层收益应近似单调；若不单调，因子可能不稳定或定义有问题。
3. 净值曲线必须扣成本；换手过高会吃掉纸面 alpha。
4. 本页 Phase 1 使用**可复现合成 A 股面板**验证流程；下一阶段接入真实行情与美股。
"""
)
