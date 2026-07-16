"""Synthetic US equity panel for offline teaching and portfolio demos.

Planted structure (intentionally different from A-share demo):
- Stronger medium-term momentum
- Clearer value (EP) and quality (ROE)
- Mild low-vol effect
- Weaker short-term reversal (US is less reversal-dominated than A-shares)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SECTORS = [
    "Technology",
    "Health Care",
    "Financials",
    "Consumer Discretionary",
    "Industrials",
    "Energy",
    "Utilities",
    "Communication",
]

# Fake but realistic-looking ticker stems
_TICKER_STEMS = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "JPM", "XOM", "JNJ", "UNH",
    "V", "MA", "PG", "HD", "CVX", "MRK", "ABBV", "PEP", "KO", "COST",
    "AVGO", "WMT", "MCD", "CSCO", "ACN", "LIN", "TMO", "ADBE", "CRM", "NFLX",
    "AMD", "INTC", "QCOM", "TXN", "AMAT", "NOW", "ISRG", "BKNG", "GE", "CAT",
    "BA", "HON", "UPS", "RTX", "SPGI", "BLK", "AXP", "GS", "MS", "SCHW",
    "C", "BAC", "WFC", "PFE", "LLY", "AMGN", "GILD", "MDT", "SYK", "BSX",
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "PCG", "ED", "XEL",
    "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA", "TTWO", "NKE", "SBUX",
]


def generate_us_panel(
    start_date: str = "2015-01-01",
    end_date: str = "2023-12-31",
    n_stocks: int = 60,
    seed: int = 7,
) -> pd.DataFrame:
    """Monthly US-style panel with fundamentals + 1M forward returns."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="ME")
    n_stocks = min(n_stocks, len(_TICKER_STEMS))
    symbols = _TICKER_STEMS[:n_stocks]
    sectors = rng.choice(SECTORS, size=n_stocks)

    true_ep = rng.normal(0, 1, size=n_stocks)
    true_mom = rng.normal(0, 1, size=n_stocks)
    true_roe = rng.normal(0, 1, size=n_stocks)
    log_mcap0 = rng.normal(23.8, 1.4, size=n_stocks)  # larger typical US names
    close = np.exp(rng.normal(4.2, 0.7, size=n_stocks))

    rows: list[dict] = []
    for t, dt in enumerate(dates):
        true_ep = 0.96 * true_ep + rng.normal(0, 0.12, size=n_stocks)
        true_mom = 0.85 * true_mom + rng.normal(0, 0.30, size=n_stocks)
        true_roe = 0.92 * true_roe + rng.normal(0, 0.18, size=n_stocks)
        log_mcap = log_mcap0 + 0.015 * t + rng.normal(0, 0.04, size=n_stocks)

        ep = true_ep + rng.normal(0, 0.35, size=n_stocks)
        bp = 0.55 * true_ep + rng.normal(0, 0.45, size=n_stocks)
        roe = true_roe + rng.normal(0, 0.30, size=n_stocks)
        mom = true_mom + rng.normal(0, 0.40, size=n_stocks)
        # US short-term reversal is weaker / noisier than A-share demo
        rev = -0.10 * true_mom + rng.normal(0, 0.70, size=n_stocks)
        vol = rng.lognormal(mean=-2.4, sigma=0.30, size=n_stocks)
        turnover = rng.lognormal(mean=-1.8, sigma=0.45, size=n_stocks)

        # Return drivers: momentum + value + quality − size − vol
        ret = (
            0.014 * true_mom
            + 0.011 * true_ep
            + 0.009 * true_roe
            - 0.005 * (log_mcap - log_mcap.mean())
            - 0.005 * ((vol - vol.mean()) / (vol.std() + 1e-8))
            + rng.normal(0, 0.07, size=n_stocks)
        )

        close = close * (1.0 + ret)
        mkt_cap = np.exp(log_mcap)

        for i, sym in enumerate(symbols):
            pe = 1.0 / max(ep[i] * 0.07 + 0.045, 0.01)
            pb = 1.0 / max(bp[i] * 0.12 + 0.18, 0.05)
            rows.append(
                {
                    "date": dt,
                    "symbol": sym,
                    "sector": sectors[i],
                    "close": float(close[i]),
                    "ret_fwd_1m": float(ret[i]),
                    "mkt_cap": float(mkt_cap[i]),
                    "pe_ttm": float(np.clip(pe, 5, 120)),
                    "pb": float(np.clip(pb, 0.5, 25)),
                    "roe": float(roe[i]),
                    "turnover": float(turnover[i]),
                    "volatility_20": float(vol[i]),
                    "momentum_raw": float(mom[i]),
                    "reverse_raw": float(rev[i]),
                    "market": "US",
                }
            )

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "symbol"]).reset_index(drop=True)
