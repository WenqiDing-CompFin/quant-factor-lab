"""Information Coefficient (IC) — first quantitative screen for a factor."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rank_ic(x: pd.Series, y: pd.Series) -> float:
    usable = pd.concat([x, y], axis=1).dropna()
    if len(usable) < 5:
        return np.nan
    # Spearman correlation is Pearson correlation of the two within-date ranks.
    return float(usable.iloc[:, 0].rank(method="average").corr(
        usable.iloc[:, 1].rank(method="average")
    ))


def factor_ic_series(factor_df: pd.DataFrame, factor: str, ret_col: str = "ret_fwd_1m") -> pd.Series:
    """Cross-sectional Rank IC each date: corr(rank(factor), rank(forward return))."""
    ic = (
        factor_df.groupby("date", group_keys=False)
        .apply(lambda g: _rank_ic(g[factor], g[ret_col]), include_groups=False)
    )
    ic.name = factor
    return ic


def summarize_ic(ic: pd.Series) -> dict:
    ic = ic.dropna()
    if ic.empty:
        return {
            "mean_ic": np.nan,
            "std_ic": np.nan,
            "icir": np.nan,
            "pos_ratio": np.nan,
            "t_stat": np.nan,
            "n": 0,
        }
    mean = float(ic.mean())
    std = float(ic.std(ddof=1))
    n = int(ic.shape[0])
    icir = mean / std if std > 0 else np.nan
    t_stat = mean / (std / np.sqrt(n)) if std > 0 else np.nan
    return {
        "mean_ic": mean,
        "std_ic": std,
        "icir": float(icir),
        "pos_ratio": float((ic > 0).mean()),
        "t_stat": float(t_stat),
        "n": n,
    }
