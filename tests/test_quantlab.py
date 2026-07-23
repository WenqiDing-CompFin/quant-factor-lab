from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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


def test_turnover_uses_return_drifted_weights() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-31"] * 2 + ["2020-02-29"] * 2),
            "symbol": ["A", "B", "A", "B"],
            "score": [2.0, 1.0, 2.0, 1.0],
            "ret_fwd_1m": [0.20, 0.0, 0.0, 0.0],
        }
    )
    result = run_long_only_backtest(
        frame, "score", top_quantile=1.0, cost_bps=0
    )
    assert result.iloc[0]["turnover"] == 1.0
    expected_pretrade_a = 0.6 / 1.1
    expected_pretrade_b = 0.5 / 1.1
    expected_turnover = 0.5 * (
        abs(0.5 - expected_pretrade_a) + abs(0.5 - expected_pretrade_b)
    )
    assert result.iloc[1]["turnover"] == pytest.approx(expected_turnover)
