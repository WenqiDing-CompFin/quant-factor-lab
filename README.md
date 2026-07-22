# Quant Factor Lab: Interactive Demo Companion

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quant-factor-lab-e5njhisnnujmsbatyy9dyz.streamlit.app/)
[![CI](https://github.com/WenqiDing-CompFin/quant-factor-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/WenqiDing-CompFin/quant-factor-lab/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> **Portfolio role:** this repository is the interactive demo and teaching layer.
> For applications and CVs, use only the flagship repository link:
> [quant-factor-research](https://github.com/WenqiDing-CompFin/quant-factor-research),
> which contains the formal methodology, failure register, tests, real-data
> validation path, and committed research artifacts.

A reproducible tutorial for exploring equity factors across **China A-shares and
US equities**. It turns economic hypotheses into testable signals, validates them
cross-sectionally, and translates them into cost-aware portfolios through an
interactive Streamlit interface.

## How the Two Quant Repositories Differ

| Repository | Primary audience | Main purpose |
|---|---|---|
| `quant-factor-research` | Reviewers, researchers, interviewers | Auditable methodology, explicit claim boundaries, regression tests, and saved research outputs |
| `quant-factor-lab` | Demo visitors and learners | Guided lessons, cross-market controls, and a deployed dashboard for exploring the workflow |

## Overview

Quant Factor Lab is designed around a simple question: can a factor survive the full path from an
economic rationale to an investable portfolio? Both markets use the same interfaces for data,
factor preparation, diagnostics, portfolio construction, and performance evaluation. Market
assumptions remain configurable, while the research logic stays comparable and auditable.

The deployed dashboard uses deterministic synthetic panels with deliberately weak factor-return
relationships. This makes every result reproducible without credentials or proprietary data and
keeps the focus on research design rather than data access.

## What the system covers

| Layer | Implementation |
|---|---|
| **Markets** | China A-share and US equity monthly cross-sections |
| **Signals** | Value, momentum, reversal, quality, size, volatility, and liquidity |
| **Preprocessing** | Cross-sectional winsorization, z-scoring, and direction alignment |
| **Diagnostics** | Rank IC, ICIR, t-statistic, positive-IC ratio, quantile returns, and factor correlation |
| **Portfolio** | Equal-weight multi-factor score and top-quantile long-only selection |
| **Backtest** | Monthly rebalancing, one-way turnover, explicit transaction costs, and equal-weight benchmark |
| **Risk** | Annualized return and volatility, Sharpe, Sortino, Calmar, drawdown, VaR, and CVaR |
| **Interface** | Interactive market controls, factor analysis, holdings, sector exposure, and CSV export |

## Research methodology

### 1. Define economically interpretable signals

Every factor has a precise definition, an expected direction, and a documented failure mode. The
catalog avoids opaque feature generation and keeps the link between hypothesis and implementation
visible in `src/quantlab/factors/catalog.py`.

### 2. Normalize each monthly cross-section

For every date, raw observations are clipped at the 2.5th and 97.5th percentiles and standardized:

```text
z(i,t,f) = [x(i,t,f) - mean_t(x_f)] / std_t(x_f)
score(i,t,f) = direction(f) * z(i,t,f)
```

After direction alignment, a higher score always represents a higher expected return. This allows
heterogeneous factors to be compared and combined on a consistent scale.

### 3. Validate factors before portfolio construction

- **Rank IC:** monthly Spearman correlation between factor score and one-month forward return.
- **ICIR:** mean Rank IC divided by its time-series standard deviation.
- **Quantile returns:** equal-weight forward returns across five score buckets to test monotonicity.
- **Correlation diagnostics:** average cross-sectional Spearman correlation to identify redundant signals.

### 4. Build a cost-aware portfolio

Selected direction-aligned factors are combined with equal weights. At each monthly rebalance, the
strategy holds the top score quantile with equal position weights. Net return is defined as:

```text
net return = gross return - one-way turnover * transaction cost
```

An equal-weight universe portfolio is evaluated on the same calendar as a transparent benchmark.

## Factor catalog

| Factor | Family | Preferred direction | Interpretation |
|---|---|---:|---|
| `ep` | Value | Higher | Earnings yield, approximated by `1 / PE` |
| `bp` | Value | Higher | Book-to-price, approximated by `1 / PB` |
| `momentum_12_1` | Momentum | Higher | Medium-term trend, excluding the most recent month |
| `reverse_1m` | Momentum | Higher | Short-term reversal signal |
| `roe` | Quality | Higher | Return on equity |
| `size_log_mcap` | Size | Lower | Log market capitalization |
| `volatility_20` | Risk | Lower | Twenty-day realized volatility proxy |
| `turnover_20` | Liquidity | Lower | Trading turnover proxy |

## Interactive dashboard

The [live application](https://quant-factor-lab-e5njhisnnujmsbatyy9dyz.streamlit.app/)
provides four connected views:

- **Performance:** strategy and benchmark NAV, plus the underwater curve.
- **Factor diagnostics:** IC scorecard, rolling IC, quantile returns, and correlation heatmap.
- **Portfolio and risk:** latest model holdings, sector exposure, tail-risk metrics, and CSV export.
- **Methodology:** selected-factor definitions and an explicit research disclaimer.

## Quick start

### Requirements

- Python 3.10 or newer
- Git

### Install and launch

```bash
git clone https://github.com/WenqiDing-CompFin/quant-factor-lab.git
cd quant-factor-lab

python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the project and run the dashboard:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
streamlit run streamlit_app.py
```

### Run the tests

```bash
pytest
```

The test suite exercises both markets end to end, checks factor diagnostics, and verifies that
transaction costs reduce terminal NAV.

### Run the research scripts

```bash
# China A-shares
python scripts/01_build_demo_data.py
python scripts/02_select_and_test_factors.py
python scripts/03_multi_factor_backtest.py

# US equities
python scripts/us_01_build_demo_data.py
python scripts/us_02_select_and_test_factors.py
python scripts/us_03_multi_factor_backtest.py
```

## Project structure

```text
quant-factor-lab/
|-- streamlit_app.py          # Unified interactive dashboard
|-- configs/                  # Market-specific research settings
|-- data/sample/              # Reproducible sample panels
|-- scripts/                  # A-share and US research entrypoints
|-- src/quantlab/
|   |-- data/                 # Data facade and synthetic generators
|   |-- factors/              # Factor catalog and preprocessing
|   |-- research/             # IC, quantile, and correlation diagnostics
|   |-- portfolio/            # Multi-factor combination
|   `-- backtest/             # Strategy, benchmark, and risk metrics
|-- tests/                    # End-to-end validation
`-- lessons/                  # Supporting research notes
```

## Research safeguards

- Fixed random seeds make both market panels deterministic.
- Forward returns are kept separate from the factor transformation pipeline.
- Factor direction is explicit and tested before combination.
- Turnover and transaction costs are reported rather than ignored.
- The benchmark shares the strategy's monthly calendar and universe.
- Synthetic data is labeled throughout the interface and documentation.

## Limitations and next steps

| Current boundary | Natural extension |
|---|---|
| Synthetic panels only | Add licensed or public production data adapters |
| Equal-weight factor blend | Compare IC-weighted, shrinkage, and risk-aware combinations |
| No sector or size neutralization | Add cross-sectional residualization and exposure constraints |
| Simple turnover cost proxy | Model spread, market impact, and capacity |
| Equal-weight benchmark | Add market-cap and factor-mimicking benchmarks |
| Single-period portfolio rule | Add walk-forward model selection and stability analysis |

These limitations are explicit by design: the current version demonstrates a clean, inspectable
research baseline before introducing additional model and data complexity.

## Data policy

The hosted application does not claim live or historical market performance. Synthetic panels are
used to verify the behavior of the research pipeline under known weak signals. A production data
loader can replace `src/quantlab/data/` without changing the factor, diagnostic, portfolio, or
backtest APIs.

## Author

**Wenqi Ding**  
GitHub: [@WenqiDing-CompFin](https://github.com/WenqiDing-CompFin)

## Disclaimer

For education and research demonstration only. Results are not live market data, are not forecasts,
and are not investment advice.

---

## 中文简介

Quant Factor Lab 是一个覆盖 A 股与美股的交互式多因子研究教程。项目使用统一代码完成因子标准化、Rank IC 与分层检验、相关性诊断、多因子组合、交易成本回测和风险分析。

在线版本采用可复现的合成面板，重点展示透明、可审计的研究流程；结果不代表真实市场收益，也不构成投资建议。正式研究方法、失败分析和可复现结果请查看 [`quant-factor-research`](https://github.com/WenqiDing-CompFin/quant-factor-research)。
