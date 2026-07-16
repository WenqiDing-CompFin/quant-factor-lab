"""Simple monthly long-only backtest for teaching."""

from __future__ import annotations

import numpy as np
import pandas as pd


def run_long_only_backtest(
    factor_df: pd.DataFrame,
    factor: str,
    top_quantile: float = 0.2,
    cost_bps: float = 10.0,
    ret_col: str = "ret_fwd_1m",
) -> pd.DataFrame:
    """Each month hold equal-weight top quantile by factor score.

    Returns a DataFrame indexed by date with columns:
    ret_gross, turnover, ret_net, nav
    """
    records = []
    prev_holdings: set[str] = set()

    for dt, g in factor_df.groupby("date"):
        g = g.dropna(subset=[factor, ret_col])
        if g.empty:
            continue
        k = max(1, int(np.ceil(len(g) * top_quantile)))
        held = set(g.nlargest(k, factor)["symbol"])
        # turnover ≈ one-way fraction of names changed
        if prev_holdings:
            turnover = 1.0 - len(held & prev_holdings) / max(len(prev_holdings), 1)
        else:
            turnover = 1.0
        ret_gross = float(g.loc[g["symbol"].isin(held), ret_col].mean())
        cost = turnover * (cost_bps / 10000.0)
        records.append(
            {
                "date": dt,
                "ret_gross": ret_gross,
                "turnover": turnover,
                "ret_net": ret_gross - cost,
                "n_holdings": len(held),
            }
        )
        prev_holdings = held

    out = pd.DataFrame(records).set_index("date").sort_index()
    out["nav"] = (1.0 + out["ret_net"]).cumprod()
    return out
