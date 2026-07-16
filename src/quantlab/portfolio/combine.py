"""Naive multi-factor combination for Phase-1 teaching."""

from __future__ import annotations

import pandas as pd


def combine_factors(
    factor_df: pd.DataFrame,
    factors: list[str],
    weights: dict[str, float] | None = None,
    out_col: str = "score_combo",
) -> pd.DataFrame:
    """Equal-weight (or custom) sum of already direction-aligned z-scores."""
    out = factor_df.copy()
    if weights is None:
        weights = {f: 1.0 / len(factors) for f in factors}
    s = 0.0
    for f in factors:
        s = s + out[f] * float(weights[f])
    out[out_col] = s
    return out
