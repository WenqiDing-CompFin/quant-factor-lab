# Quant Factor Lab

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quant-factor-lab-e5njhisnnujmsbatyy9dyz.streamlit.app/)

A deployable, cross-market factor research workbench for **China A-shares and US equities**.  
It turns an economic hypothesis into a cost-aware portfolio through one shared research stack.

---

## Motivation

Factor investing is a cornerstone of quantitative equity strategies. This project builds a **complete, reproducible research framework** to construct, evaluate, and diagnose cross-sectional equity factors across two major markets. The entire pipeline — from raw factor definition to portfolio backtest — can be run by anyone without API keys, making the methodology fully auditable.

---

## Key Features

| Module | What it does |
|--------|-------------|
| **Factor Catalog** | 8 factor definitions (value, momentum, quality, size, risk, liquidity) with economic rationale and known pitfalls |
| **Data Pipeline** | Reproducible synthetic panels for both A-shares and US equities, with planted weak signals for realistic IC behavior |
| **Factor Diagnostics** | Cross-sectional Rank IC, ICIR, t-statistics, positive-IC ratio, Spearman correlation matrix |
| **Quantile Analysis** | Layer returns to verify monotonicity — a core sanity check for factor validity |
| **Portfolio Construction** | Equal-weight multi-factor composite score → top-quantile long-only portfolio |
| **Cost-Aware Backtest** | Explicit one-way transaction cost modeling, turnover tracking, NAV evolution |
| **Risk Metrics** | Sharpe, Sortino, Calmar, maximum drawdown, monthly 95% CVaR, positive-month ratio |
| **Interactive Dashboard** | Unified Streamlit UI for both markets, with sector exposure analysis and CSV export |

---

## Research Pipeline


## Quick Start

### Run locally

### Run tests

---

## Project Structure

---

## Factor Catalog

| Factor | Family | Direction | Economic Intuition |
|--------|---------|-----------|-------------------|
| `ep` | Value | Higher is better | Undervalued earnings potential (earnings yield) |
| `bp` | Value | Higher is better | Classic Fama–French HML value premium |
| `momentum_12_1` | Momentum | Higher is better | Medium-term trend persistence (skip recent month) |
| `reverse_1m` | Momentum | Higher is better | Short-term overreaction reversal |
| `volatility_20` | Risk | Lower is better | Low-volatility anomaly |
| `turnover_20` | Liquidity | Lower is better | Overheated trading signal |
| `roe` | Quality | Higher is better | Sustainable high-quality earnings |
| `size_log_mcap` | Size | Lower is better | Small-cap premium / liquidity compensation |

---

## Data Policy

The deployed application uses **deterministic synthetic panels with planted weak signals**. This keeps the research reproducible, avoids redistribution restrictions, and makes the full methodology auditable without an API key.

**Why synthetic first?**
- ✅ Anyone can run the complete research pipeline in one click
- ✅ No API key / network required — ideal for admissions portfolio review
- ✅ Known factor–return relationships let you verify each research step
- 🔄 Production adapters can replace `src/quantlab/data/` without changing factor, research, portfolio, or backtest APIs

---

## Limitations & Planned Extensions

| Current Limitation | Planned Next Step |
|-------------------|-------------------|
| Equal-weight combination only | Optimized weighting (IC-weighted / risk-parity) |
| No sector/market-cap neutralization | Cross-sectional OLS neutralization by sector & size |
| Synthetic data only | Production loader for Wind / Compustat / CRSP |
| No transaction cost decay modeling | Capacity- and liquidity-aware cost function |
| Equal-weight benchmark | Market-cap-weighted / factor-mimicking benchmarks |

---

## Disclaimer

**For education and research demonstration only.** The displayed results are not live market data, are not forecasts, and are not investment advice.

---

## Author

**Wenqi Ding**  
GitHub: [@WenqiDing-CompFin](https://github.com/WenqiDing-CompFin)
