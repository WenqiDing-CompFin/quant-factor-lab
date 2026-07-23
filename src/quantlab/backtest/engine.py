"""Monthly portfolio engines used by the research dashboard."""

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
    pretrade_weights: dict[str, float] = {}

    for dt, g in factor_df.groupby("date"):
        g = g.dropna(subset=[factor, ret_col])
        if g.empty:
            continue
        k = max(1, int(np.ceil(len(g) * top_quantile)))
        selected = g.nlargest(k, factor)[["symbol", ret_col]].copy()
        target_weight = 1.0 / k
        target_weights = dict.fromkeys(selected["symbol"], target_weight)
        if pretrade_weights:
            names = set(pretrade_weights).union(target_weights)
            turnover = 0.5 * sum(
                abs(target_weights.get(name, 0.0) - pretrade_weights.get(name, 0.0))
                for name in names
            )
        else:
            turnover = sum(target_weights.values())
        ret_gross = float(selected[ret_col].mean())
        cost = turnover * (cost_bps / 10000.0)
        records.append(
            {
                "date": dt,
                "ret_gross": ret_gross,
                "turnover": turnover,
                "ret_net": ret_gross - cost,
                "n_holdings": len(selected),
            }
        )
        end_values = {
            row.symbol: target_weight * (1.0 + row.return_value)
            for row in selected.rename(columns={ret_col: "return_value"}).itertuples(
                index=False
            )
        }
        total_end_value = sum(end_values.values())
        pretrade_weights = {
            symbol: value / total_end_value for symbol, value in end_values.items()
        }

    out = pd.DataFrame(records).set_index("date").sort_index()
    out["nav"] = (1.0 + out["ret_net"]).cumprod()
    return out


def run_equal_weight_benchmark(
    factor_df: pd.DataFrame,
    ret_col: str = "ret_fwd_1m",
) -> pd.DataFrame:
    """Return an equal-weight universe benchmark on the same monthly calendar."""
    monthly = (
        factor_df.dropna(subset=[ret_col])
        .groupby("date", sort=True)[ret_col]
        .mean()
        .rename("ret_net")
        .to_frame()
    )
    monthly["ret_gross"] = monthly["ret_net"]
    monthly["turnover"] = 0.0
    monthly["n_holdings"] = factor_df.groupby("date")["symbol"].nunique()
    monthly["nav"] = (1.0 + monthly["ret_net"]).cumprod()
    return monthly
