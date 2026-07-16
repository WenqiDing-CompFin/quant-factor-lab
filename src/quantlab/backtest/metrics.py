"""Performance metrics for monthly NAV / return series."""

from __future__ import annotations

import numpy as np
import pandas as pd


def performance_stats(bt: pd.DataFrame, ret_col: str = "ret_net") -> dict:
    r = bt[ret_col].dropna()
    if r.empty:
        return {}
    nav = (1.0 + r).cumprod()
    total = float(nav.iloc[-1] - 1.0)
    n_years = len(r) / 12.0
    ann_ret = float(nav.iloc[-1] ** (1 / n_years) - 1) if n_years > 0 else np.nan
    ann_vol = float(r.std(ddof=1) * np.sqrt(12))
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    dd = nav / nav.cummax() - 1.0
    max_dd = float(dd.min())
    return {
        "total_return": total,
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": float(sharpe),
        "max_drawdown": max_dd,
        "avg_turnover": float(bt["turnover"].mean()) if "turnover" in bt else np.nan,
        "n_months": int(len(r)),
    }
