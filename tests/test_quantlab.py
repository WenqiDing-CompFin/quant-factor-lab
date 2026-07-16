from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.backtest import (
    performance_stats,
    run_equal_weight_benchmark,
    run_long_only_backtest,
)
from quantlab.data import generate_ashare_panel, generate_us_panel
from quantlab.factors import compute_factors
from quantlab.portfolio import combine_factors
from quantlab.research import factor_corr_matrix, factor_ic_series, layer_returns


FACTORS = ["ep", "momentum_12_1", "roe", "volatility_20"]


def _research_frame(panel: pd.DataFrame) -> pd.DataFrame:
    factor_df = compute_factors(panel, FACTORS)
    return combine_factors(factor_df, FACTORS)


def test_both_markets_run_end_to_end() -> None:
    generators = [generate_ashare_panel, generate_us_panel]
    for generator in generators:
        panel = generator(start_date="2020-01-01", end_date="2022-12-31", n_stocks=30)
        combined = _research_frame(panel)
        strategy = run_long_only_backtest(combined, "score_combo", cost_bps=8)
        benchmark = run_equal_weight_benchmark(combined)
        stats = performance_stats(strategy)

        assert len(strategy) == 36
        assert strategy.index.equals(benchmark.index)
        assert strategy["nav"].gt(0).all()
        assert 0 <= stats["positive_months"] <= 1
        assert stats["max_drawdown"] <= 0


def test_factor_diagnostics_are_well_formed() -> None:
    panel = generate_ashare_panel(
        start_date="2020-01-01", end_date="2022-12-31", n_stocks=30, seed=4
    )
    factor_df = compute_factors(panel, FACTORS)
    ic = factor_ic_series(factor_df, "ep")
    layers = layer_returns(factor_df, "ep", n_layers=5)
    corr = factor_corr_matrix(factor_df, FACTORS)

    assert len(ic) == 36
    assert "long_short" in layers
    assert corr.shape == (len(FACTORS), len(FACTORS))
    assert np.allclose(np.diag(corr), 1.0)


def test_transaction_cost_reduces_nav() -> None:
    panel = generate_us_panel(
        start_date="2020-01-01", end_date="2022-12-31", n_stocks=30, seed=9
    )
    combined = _research_frame(panel)
    free = run_long_only_backtest(combined, "score_combo", cost_bps=0)
    costly = run_long_only_backtest(combined, "score_combo", cost_bps=25)

    assert costly["nav"].iloc[-1] < free["nav"].iloc[-1]
