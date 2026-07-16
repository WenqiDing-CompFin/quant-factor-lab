"""Synthetic A-share-like panel for offline teaching and demos.

Why synthetic first?
- No API key / network required — reproducible for GitHub and offline research
- Known factor–return relationships so you can verify the research pipeline
- Later swap this module for akshare / Wind / Tushare loaders without changing
  factor / IC / backtest code
"""

from __future__ import annotations

import numpy as np
import pandas as pd


SECTORS = ["银行", "白酒", "新能源", "医药", "电子", "地产", "基建", "消费"]


def generate_ashare_panel(
    start_date: str = "2018-01-01",
    end_date: str = "2023-12-31",
    n_stocks: int = 80,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a monthly stock panel with fundamentals + returns.

    Columns
    -------
    date, symbol, sector, close, ret_fwd_1m, mkt_cap, pe_ttm, pb,
    roe, turnover, volume, earnings_yield, book_to_price
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="ME")
    symbols = [f"{i:06d}.SZ" if i % 2 == 0 else f"{i:06d}.SH" for i in range(1, n_stocks + 1)]

    rows: list[dict] = []
    # Latent true exposures that drive returns (oracle — for teaching only)
    true_ep = rng.normal(0, 1, size=n_stocks)
    true_mom = rng.normal(0, 1, size=n_stocks)
    true_roe = rng.normal(0, 1, size=n_stocks)
    log_mcap0 = rng.normal(22.5, 1.2, size=n_stocks)  # ~ e^22.5 元量级市值
    sectors = rng.choice(SECTORS, size=n_stocks)

    close = np.exp(rng.normal(3.0, 0.5, size=n_stocks))  # price level

    for t, dt in enumerate(dates):
        # Slow drift in latent factors
        true_ep = 0.95 * true_ep + rng.normal(0, 0.15, size=n_stocks)
        true_mom = 0.80 * true_mom + rng.normal(0, 0.35, size=n_stocks)
        true_roe = 0.90 * true_roe + rng.normal(0, 0.20, size=n_stocks)
        log_mcap = log_mcap0 + 0.02 * t + rng.normal(0, 0.05, size=n_stocks)

        # Observed noisy signals
        ep = true_ep + rng.normal(0, 0.4, size=n_stocks)
        bp = 0.6 * true_ep + rng.normal(0, 0.5, size=n_stocks)
        roe = true_roe + rng.normal(0, 0.35, size=n_stocks)
        mom = true_mom + rng.normal(0, 0.45, size=n_stocks)
        rev = -0.3 * true_mom + rng.normal(0, 0.6, size=n_stocks)
        vol = rng.lognormal(mean=-2.2, sigma=0.35, size=n_stocks)
        turnover = rng.lognormal(mean=-1.5, sigma=0.5, size=n_stocks)

        # Next-month return: value + momentum + quality − size − vol + noise
        # Coefficients chosen so IC is typically ~0.03–0.08 (realistic weak signal)
        ret = (
            0.012 * true_ep
            + 0.010 * true_mom
            + 0.008 * true_roe
            - 0.006 * (log_mcap - log_mcap.mean())
            - 0.004 * ((vol - vol.mean()) / vol.std())
            + rng.normal(0, 0.08, size=n_stocks)
        )

        close = close * (1.0 + ret)
        mkt_cap = np.exp(log_mcap)

        for i, sym in enumerate(symbols):
            pe = 1.0 / max(ep[i] * 0.08 + 0.05, 0.01)  # rough map
            pb = 1.0 / max(bp[i] * 0.15 + 0.20, 0.05)
            rows.append(
                {
                    "date": dt,
                    "symbol": sym,
                    "sector": sectors[i],
                    "close": float(close[i]),
                    "ret_fwd_1m": float(ret[i]),
                    "mkt_cap": float(mkt_cap[i]),
                    "pe_ttm": float(np.clip(pe, 3, 200)),
                    "pb": float(np.clip(pb, 0.3, 30)),
                    "roe": float(roe[i]),
                    "turnover": float(turnover[i]),
                    "volatility_20": float(vol[i]),
                    "momentum_raw": float(mom[i]),
                    "reverse_raw": float(rev[i]),
                }
            )

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "symbol"]).reset_index(drop=True)
    return df
