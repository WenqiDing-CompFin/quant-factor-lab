"""Factor correlation — detect redundant signals before combining."""

from __future__ import annotations

import pandas as pd


def factor_corr_matrix(factor_df: pd.DataFrame, factors: list[str]) -> pd.DataFrame:
    """Average cross-sectional Spearman correlation across dates."""
    mats = []
    for _, g in factor_df.groupby("date"):
        if g[factors].notna().sum().min() < 5:
            continue
        mats.append(g[factors].corr(method="spearman"))
    if not mats:
        return pd.DataFrame(index=factors, columns=factors, dtype=float)
    return sum(mats) / len(mats)
