"""Quantile-layer returns — the second classic factor test."""

from __future__ import annotations

import numpy as np
import pandas as pd


def layer_returns(
    factor_df: pd.DataFrame,
    factor: str,
    n_layers: int = 5,
    ret_col: str = "ret_fwd_1m",
) -> pd.DataFrame:
    """Equal-weight mean forward return by factor quantile each date."""

    def _one(g: pd.DataFrame) -> pd.Series:
        try:
            q = pd.qcut(g[factor], n_layers, labels=False, duplicates="drop")
        except ValueError:
            return pd.Series(dtype=float)
        tmp = g.assign(layer=q)
        return tmp.groupby("layer")[ret_col].mean()

    layered = factor_df.groupby("date", group_keys=True).apply(_one, include_groups=False)
    if isinstance(layered, pd.Series):
        layered = layered.unstack("layer")
    layered.columns = [f"Q{int(c) + 1}" for c in layered.columns]
    # Long top / short bottom (after direction flip, Qn should beat Q1)
    if layered.shape[1] >= 2:
        layered["long_short"] = layered.iloc[:, -1] - layered.iloc[:, 0]
    return layered


def layer_summary(layered: pd.DataFrame) -> pd.Series:
    return layered.mean()
