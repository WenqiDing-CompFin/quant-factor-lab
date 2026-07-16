# Quant Factor Lab

[**Open the live application**](https://quant-factor-lab-e5njhisnnujmsbatyy9dyz.streamlit.app/)

A deployable cross-market factor research workbench for **China A-shares and US equities**.
It turns an economic hypothesis into a cost-aware portfolio through one shared research stack.

## What it includes

- Cross-sectional value, momentum, quality, size, volatility, and liquidity factors
- Winsorization and direction-aligned z-score normalization
- Rank IC, ICIR, t-statistics, positive-IC ratio, and quantile return tests
- Factor redundancy diagnostics with average Spearman correlation
- Monthly long-only portfolio construction with explicit transaction costs
- Equal-weight benchmark, NAV, drawdown, turnover, VaR, CVaR, Sharpe, Sortino, and Calmar
- A unified Streamlit dashboard for both markets
- Reproducible synthetic panels so the full project runs without API keys

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
streamlit run streamlit_app.py
```

Run the tests with:

```bash
pip install -e ".[dev]"
pytest
```

## Research flow

```text
Economic story
    -> raw factor definition
    -> cross-sectional winsorization and z-score
    -> Rank IC / ICIR and quantile tests
    -> correlation diagnostics
    -> equal-weight multi-factor score
    -> top-quantile portfolio
    -> transaction-cost-aware backtest
```

## Project structure

```text
streamlit_app.py     # Unified deployed dashboard
configs/             # A-share and US research settings
src/quantlab/
  data/              # Reproducible market-like panels
  factors/           # Factor catalog and transformations
  research/          # IC, quantile, and correlation diagnostics
  portfolio/         # Multi-factor combination
  backtest/          # Strategy, benchmark, and risk metrics
tests/               # End-to-end research tests
lessons/             # Supporting factor-research notes
```

## Data policy

The deployed application intentionally uses deterministic synthetic panels with planted weak
signals. This keeps the research reproducible, avoids redistribution restrictions, and makes the
methodology auditable without an API key. Production adapters can replace `src/quantlab/data/`
without changing the factor, research, portfolio, or backtest APIs.

## Disclaimer

For education and research demonstration only. The displayed results are not live market data,
are not forecasts, and are not investment advice.

---

## 中文说明

这是一个覆盖 **A 股与美股** 的跨市场多因子研究项目。统一界面展示因子 IC、分层收益、
相关性、组合净值、回撤、换手率和尾部风险。在线版本使用可复现的合成面板，确保任何人
无需 API Key 即可运行和审阅完整研究流程；结果不代表真实市场收益，也不构成投资建议。
