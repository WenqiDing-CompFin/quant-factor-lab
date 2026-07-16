# Lesson 04 — US equities module

You already have the A-share teaching track. This module reuses the **same research API** on a US-style panel.

## What is the same
- Factor catalog / winsorize / z-score / direction flip  
- Rank IC, ICIR, quantile layers  
- Equal-weight multi-factor score  
- Cost-aware monthly long-only backtest  
- Streamlit visualization  

## What is intentionally different (US vs A-share demo)
| Topic | A-share demo | US demo |
|---|---|---|
| Short-term reversal | Often stronger | Weaker / noisier |
| 12-1 momentum | Mixed | Stronger planted signal |
| Costs | Higher bps default | Lower bps default |
| Tickers / sectors | `.SH/.SZ` + CN sectors | US tickers + GICS-like |

## Run
```bash
python scripts/us_01_build_demo_data.py
python scripts/us_02_select_and_test_factors.py
python scripts/us_03_multi_factor_backtest.py
streamlit run app/streamlit_us.py
```

## Admissions talking point
> “I built a market-agnostic factor research stack and instantiated it on both China A-shares and US equities, highlighting institutional differences such as reversal vs momentum and transaction costs.”
