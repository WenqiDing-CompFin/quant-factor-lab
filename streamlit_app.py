"""Unified A-share and US equity factor research dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from quantlab.backtest import (  # noqa: E402
    performance_stats,
    run_equal_weight_benchmark,
    run_long_only_backtest,
)
from quantlab.data.loader import load_config, load_panel  # noqa: E402
from quantlab.factors import FACTOR_CATALOG, compute_factors, list_factors  # noqa: E402
from quantlab.portfolio import combine_factors  # noqa: E402
from quantlab.research import (  # noqa: E402
    factor_corr_matrix,
    factor_ic_series,
    layer_returns,
    summarize_ic,
)

MARKETS = {
    "China A-shares": {
        "config": "ashare_demo.yaml",
        "code": "CN",
        "cost": 10,
        "description": "China A-share monthly cross-section",
    },
    "US equities": {
        "config": "us_demo.yaml",
        "code": "US",
        "cost": 5,
        "description": "US large-cap monthly cross-section",
    },
}

COLORS = {
    "strategy": "#167D59",
    "benchmark": "#C65D3D",
    "neutral": "#687076",
    "gold": "#B28704",
    "grid": "rgba(104, 112, 118, 0.18)",
}

st.set_page_config(
    page_title="Quant Factor Lab",
    page_icon=":material/query_stats:",
    layout="wide",
)


def _plot_layout(title: str, y_title: str = "") -> dict:
    return {
        "title": {"text": title, "x": 0, "font": {"size": 17}},
        "height": 410,
        "margin": {"l": 16, "r": 16, "t": 54, "b": 28},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, Arial, sans-serif", "color": "#27312C"},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": 1.12, "x": 1, "xanchor": "right"},
        "xaxis": {"showgrid": False, "title": ""},
        "yaxis": {"gridcolor": COLORS["grid"], "title": y_title, "zeroline": False},
    }


@st.cache_data(show_spinner=False)
def load_market(market_name: str) -> tuple[dict, pd.DataFrame]:
    config_path = ROOT / "configs" / MARKETS[market_name]["config"]
    return load_config(config_path), load_panel(config_path, source="synthetic")


@st.cache_data(show_spinner=False)
def run_research(
    market_name: str,
    factors: tuple[str, ...],
    top_quantile: float,
    cost_bps: int,
) -> dict:
    _, panel = load_market(market_name)
    factor_df = compute_factors(panel, factor_names=list(factors))
    combined = combine_factors(factor_df, list(factors))
    strategy = run_long_only_backtest(
        combined,
        "score_combo",
        top_quantile=top_quantile,
        cost_bps=cost_bps,
    )
    benchmark = run_equal_weight_benchmark(combined)

    ic_series: dict[str, pd.Series] = {}
    ic_rows: list[dict] = []
    for factor in factors:
        series = factor_ic_series(factor_df, factor)
        summary = summarize_ic(series)
        summary["factor"] = factor
        ic_series[factor] = series
        ic_rows.append(summary)

    latest_date = combined["date"].max()
    latest = combined.loc[combined["date"].eq(latest_date)].nlargest(
        max(1, int(np.ceil(combined["symbol"].nunique() * top_quantile))),
        "score_combo",
    )
    return {
        "panel": panel,
        "factor_df": factor_df,
        "combined": combined,
        "strategy": strategy,
        "benchmark": benchmark,
        "strategy_stats": performance_stats(strategy),
        "benchmark_stats": performance_stats(benchmark),
        "ic_table": pd.DataFrame(ic_rows).set_index("factor"),
        "ic_series": pd.DataFrame(ic_series),
        "correlation": factor_corr_matrix(factor_df, list(factors)),
        "latest": latest,
        "latest_date": latest_date,
    }


def drawdown(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1.0


def pct(value: float, digits: int = 1) -> str:
    return "n/a" if pd.isna(value) else f"{value:.{digits}%}"


st.title("Quant factor lab")
st.caption("Cross-market factor research for China A-shares and US equities")
with st.container(horizontal=True):
    st.badge("Synthetic demo", icon=":material/science:", color="orange")
    st.badge("Deterministic", icon=":material/check_circle:", color="green")
    st.badge("Monthly", icon=":material/calendar_month:", color="gray")

market = st.segmented_control(
    "Market universe",
    options=list(MARKETS),
    default="China A-shares",
    label_visibility="collapsed",
)
market = market or "China A-shares"
cfg, raw_panel = load_market(market)

with st.sidebar:
    st.header("Research controls", anchor=False)
    st.caption(MARKETS[market]["description"])
    categories = sorted({spec.category for spec in list_factors()})
    chosen_categories = st.pills(
        "Factor families",
        categories,
        default=categories,
        selection_mode="multi",
    )
    candidates = [spec.name for spec in list_factors() if spec.category in chosen_categories]
    default_factors = [factor for factor in cfg["factors"] if factor in candidates][:5]
    selected = st.multiselect("Factors", candidates, default=default_factors)
    top_percent = st.slider(
        "Portfolio size",
        min_value=10,
        max_value=40,
        value=int(round(float(cfg["top_quantile"]) * 100)),
        step=5,
        format="Top %d%%",
    )
    top_quantile = top_percent / 100
    cost_bps = st.slider(
        "One-way transaction cost",
        min_value=0,
        max_value=50,
        value=int(MARKETS[market]["cost"]),
        step=1,
        format="%d bps",
    )
    st.caption("Monthly rebalance · equal-weight selected names · zero risk-free rate")
    st.link_button(
        "Open audited research",
        "https://github.com/WenqiDing-CompFin/quant-factor-research",
        icon=":material/open_in_new:",
        width="stretch",
    )

if not selected:
    st.info("Select at least one factor to run the research pipeline.")
    st.stop()

result = run_research(market, tuple(selected), top_quantile, cost_bps)
strategy = result["strategy"]
benchmark = result["benchmark"]
stats = result["strategy_stats"]
bench_stats = result["benchmark_stats"]

st.caption(
    f'Reproducible synthetic {MARKETS[market]["code"]} panel · '
    f'{raw_panel["symbol"].nunique()} securities · {len(strategy)} monthly observations · '
    "not live market data"
)

with st.container(horizontal=True):
    st.metric(
        "Annualized return",
        pct(stats["ann_return"]),
        pct(stats["ann_return"] - bench_stats["ann_return"]),
        help="Strategy CAGR; delta is versus the equal-weight universe.",
        border=True,
    )
    st.metric(
        "Sharpe ratio",
        f'{stats["sharpe"]:.2f}',
        help="Annualized arithmetic return / volatility.",
        border=True,
    )
    st.metric(
        "Maximum drawdown",
        pct(stats["max_drawdown"]),
        delta_color="inverse",
        border=True,
    )
    st.metric(
        "Average turnover",
        pct(stats["avg_turnover"]),
        help="One-way monthly name turnover.",
        border=True,
    )

overview_tab, factors_tab, portfolio_tab, method_tab = st.tabs(
    ["Performance", "Factor diagnostics", "Portfolio & risk", "Methodology"]
)

with overview_tab:
    nav_fig = go.Figure()
    nav_fig.add_trace(
        go.Scatter(
            x=strategy.index,
            y=strategy["nav"],
            name="Multi-factor strategy",
            mode="lines",
            line={"color": COLORS["strategy"], "width": 2.5},
        )
    )
    nav_fig.add_trace(
        go.Scatter(
            x=benchmark.index,
            y=benchmark["nav"],
            name="Equal-weight universe",
            mode="lines",
            line={"color": COLORS["benchmark"], "width": 2, "dash": "dot"},
        )
    )
    nav_fig.update_layout(**_plot_layout("Cumulative net asset value", "Growth of 1.00"))
    st.plotly_chart(nav_fig, width="stretch", config={"displayModeBar": False})

    dd_fig = go.Figure()
    dd_fig.add_trace(
        go.Scatter(
            x=strategy.index,
            y=drawdown(strategy["nav"]),
            mode="lines",
            name="Strategy drawdown",
            fill="tozeroy",
            line={"color": COLORS["benchmark"], "width": 1.5},
            fillcolor="rgba(198, 93, 61, 0.18)",
        )
    )
    dd_fig.update_layout(**_plot_layout("Underwater curve", "Drawdown"))
    dd_fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(dd_fig, width="stretch", config={"displayModeBar": False})

with factors_tab:
    ic_table = result["ic_table"]["mean_ic icir t_stat pos_ratio n".split()].sort_values(
        "icir", ascending=False
    ).reset_index()
    st.subheader("Rank IC scorecard")
    st.dataframe(
        ic_table,
        column_config={
            "factor": st.column_config.TextColumn("Factor", pinned=True),
            "mean_ic": st.column_config.NumberColumn("Mean IC", format="%+.4f"),
            "icir": st.column_config.NumberColumn("ICIR", format="%+.3f"),
            "t_stat": st.column_config.NumberColumn("t-stat", format="%+.2f"),
            "pos_ratio": st.column_config.NumberColumn("Positive IC", format="percent"),
            "n": st.column_config.NumberColumn("Months", format="%d"),
        },
        width="stretch",
        hide_index=True,
    )

    diag_left, diag_right = st.columns(2)
    with diag_left:
        ic_fig = go.Figure()
        palette = [COLORS["strategy"], COLORS["benchmark"], COLORS["gold"], COLORS["neutral"]]
        for index, factor in enumerate(result["ic_series"].columns):
            ic_fig.add_trace(
                go.Scatter(
                    x=result["ic_series"].index,
                    y=result["ic_series"][factor].rolling(6, min_periods=3).mean(),
                    name=factor,
                    mode="lines",
                    line={"color": palette[index % len(palette)], "width": 1.7},
                )
            )
        ic_fig.add_hline(y=0, line_width=1, line_color=COLORS["neutral"])
        ic_fig.update_layout(**_plot_layout("Six-month rolling Rank IC", "Rank IC"))
        st.plotly_chart(ic_fig, width="stretch", config={"displayModeBar": False})

    with diag_right:
        corr = result["correlation"]
        corr_fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.index,
                zmin=-1,
                zmax=1,
                colorscale=[[0, "#C65D3D"], [0.5, "#F2F2EE"], [1, "#167D59"]],
                colorbar={"title": "rho"},
                text=np.round(corr.values, 2),
                texttemplate="%{text}",
                hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>",
            )
        )
        corr_fig.update_layout(**_plot_layout("Average cross-sectional correlation"))
        corr_fig.update_yaxes(autorange="reversed")
        st.plotly_chart(corr_fig, width="stretch", config={"displayModeBar": False})

    layer_factor = st.selectbox("Inspect quantile monotonicity", selected, index=0)
    layered = layer_returns(result["factor_df"], layer_factor, n_layers=5)
    layer_means = layered.drop(columns="long_short", errors="ignore").mean()
    layer_fig = go.Figure(
        go.Bar(
            x=layer_means.index,
            y=layer_means.values,
            marker_color=[COLORS["neutral"]] * 4 + [COLORS["strategy"]],
            hovertemplate="%{x}: %{y:.2%}<extra></extra>",
        )
    )
    layer_fig.update_layout(**_plot_layout(f"Forward return by {layer_factor} quantile", "Mean monthly return"))
    layer_fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(layer_fig, width="stretch", config={"displayModeBar": False})

with portfolio_tab:
    with st.container(horizontal=True):
        st.metric("Annualized volatility", pct(stats["ann_vol"]), border=True)
        st.metric("Sortino ratio", f'{stats["sortino"]:.2f}', border=True)
        st.metric("Monthly 95% CVaR", pct(stats["monthly_cvar_95"]), border=True)
        st.metric("Positive months", pct(stats["positive_months"]), border=True)

    latest = result["latest"].copy()
    display_columns = ["symbol", "sector", "score_combo"] + list(selected)
    latest_display = latest[display_columns].sort_values("score_combo", ascending=False)
    st.subheader(f'Latest model portfolio · {result["latest_date"]:%Y-%m-%d}')
    st.dataframe(
        latest_display,
        column_config={
            column: st.column_config.NumberColumn(format="%+.2f")
            for column in display_columns[2:]
        },
        width="stretch",
        hide_index=True,
    )

    sector_weight = latest["sector"].value_counts(normalize=True).sort_values()
    sector_fig = go.Figure(
        go.Bar(
            x=sector_weight.values,
            y=sector_weight.index,
            orientation="h",
            marker_color=COLORS["gold"],
            hovertemplate="%{y}: %{x:.1%}<extra></extra>",
        )
    )
    sector_fig.update_layout(**_plot_layout("Portfolio sector exposure", "Weight"))
    sector_fig.update_xaxes(tickformat=".0%", gridcolor=COLORS["grid"])
    st.plotly_chart(sector_fig, width="stretch", config={"displayModeBar": False})

    export = strategy.reset_index().merge(
        benchmark[["nav"]].rename(columns={"nav": "benchmark_nav"}).reset_index(),
        on="date",
        how="left",
    )
    st.download_button(
        "Download backtest CSV",
        data=export.to_csv(index=False).encode("utf-8"),
        file_name=f'{MARKETS[market]["code"].lower()}_factor_backtest.csv',
        mime="text/csv",
        icon=":material/download:",
    )

with method_tab:
    st.subheader("Research pipeline")
    st.markdown(
        "**Economic hypothesis → winsorization → cross-sectional z-score → Rank IC → "
        "quantile sorts → factor correlation → equal-weight composite → cost-aware backtest**"
    )
    st.caption(
        "Scores are direction-aligned, so a higher value always means a higher expected return. "
        "The portfolio holds the top cross-sectional quantile and rebalances monthly."
    )

    factor_reference = pd.DataFrame(
        [
            {
                "factor": name,
                "family": FACTOR_CATALOG[name].category,
                "definition": FACTOR_CATALOG[name].description_en,
                "preferred direction": "higher" if FACTOR_CATALOG[name].direction > 0 else "lower",
            }
            for name in selected
        ]
    )
    st.dataframe(factor_reference, width="stretch", hide_index=True)
    st.warning(
        "Educational research only. The deployed app uses reproducible synthetic panels with planted "
        "weak signals. Results are not live, are not forecasts, and are not investment advice.",
        icon=":material/warning:",
    )
    st.link_button(
        "Review official real-market evidence",
        "https://github.com/WenqiDing-CompFin/quant-factor-research/tree/main/results/public_factors/latest",
        icon=":material/open_in_new:",
    )
