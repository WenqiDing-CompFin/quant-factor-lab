"""Compute and standardize cross-sectional factors."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .catalog import FACTOR_CATALOG


def winsorize_cross_section(s: pd.Series, lower: float = 0.025, upper: float = 0.975) -> pd.Series:
    lo, hi = s.quantile(lower), s.quantile(upper)
    return s.clip(lo, hi)


def zscore_cross_section(s: pd.Series) -> pd.Series:
    mu, sigma = s.mean(), s.std(ddof=0)
    if sigma == 0 or np.isnan(sigma):
        return s * 0.0
    return (s - mu) / sigma


def _prepare_raw(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.copy()
    df["ep"] = 1.0 / df["pe_ttm"]
    df["bp"] = 1.0 / df["pb"]
    df["momentum_12_1"] = df["momentum_raw"]
    df["reverse_1m"] = df["reverse_raw"]
    df["size_log_mcap"] = np.log(df["mkt_cap"])
    # volatility_20, turnover_20, roe already present (turnover renamed)
    df["turnover_20"] = df["turnover"]
    return df


def compute_factors(
    panel: pd.DataFrame,
    factor_names: list[str] | None = None,
    standardize: bool = True,
) -> pd.DataFrame:
    """Return long panel with columns: date, symbol, sector, ret_fwd_1m, factors...

    Standardization is cross-sectional (by date), then multiplied by factor direction
    so that *higher score always means expected higher return*.
    """
    names = factor_names or list(FACTOR_CATALOG.keys())
    unknown = set(names) - set(FACTOR_CATALOG)
    if unknown:
        raise ValueError(f"Unknown factors: {sorted(unknown)}")

    df = _prepare_raw(panel)
    keep = ["date", "symbol", "sector", "ret_fwd_1m", "mkt_cap"] + names
    out = df[["date", "symbol", "sector", "ret_fwd_1m", "mkt_cap"]].copy()

    for name in names:
        spec = FACTOR_CATALOG[name]
        raw = df.groupby("date", group_keys=False)[name].transform(winsorize_cross_section)
        if standardize:
            z = df.assign(**{name: raw}).groupby("date", group_keys=False)[name].transform(
                zscore_cross_section
            )
            out[name] = z * spec.direction
        else:
            out[name] = raw * spec.direction

    return out[keep]
