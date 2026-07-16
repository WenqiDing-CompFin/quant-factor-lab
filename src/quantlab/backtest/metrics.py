"""Performance and downside-risk metrics for monthly return series."""

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
    sharpe = float(r.mean() * 12 / ann_vol) if ann_vol > 0 else np.nan
    dd = nav / nav.cummax() - 1.0
    max_dd = float(dd.min())
    downside = r[r < 0]
    downside_vol = float(downside.std(ddof=1) * np.sqrt(12)) if len(downside) > 1 else np.nan
    sortino = float(r.mean() * 12 / downside_vol) if downside_vol > 0 else np.nan
    calmar = float(ann_ret / abs(max_dd)) if max_dd < 0 else np.nan
    var_95 = float(r.quantile(0.05))
    tail = r[r <= var_95]
    return {
        "total_return": total,
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": float(sharpe),
        "sortino": sortino,
        "calmar": calmar,
        "max_drawdown": max_dd,
        "monthly_var_95": var_95,
        "monthly_cvar_95": float(tail.mean()) if not tail.empty else np.nan,
        "positive_months": float((r > 0).mean()),
        "avg_turnover": float(bt["turnover"].mean()) if "turnover" in bt else np.nan,
        "n_months": int(len(r)),
    }
