"""Combine surviving factors and backtest the composite score."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantlab.backtest import performance_stats, run_long_only_backtest
from quantlab.data.loader import load_config, load_panel
from quantlab.factors import compute_factors
from quantlab.portfolio import combine_factors
from quantlab.research import factor_ic_series, summarize_ic


def main() -> None:
    cfg = load_config(ROOT / "configs" / "ashare_demo.yaml")
    panel = load_panel(ROOT / "configs" / "ashare_demo.yaml", source="synthetic")
    names = cfg["factors"]
    fdf = compute_factors(panel, factor_names=names)

    # Auto-select by ICIR
    ranked = []
    for name in names:
        s = summarize_ic(factor_ic_series(fdf, name))
        ranked.append((name, s["icir"]))
    ranked.sort(key=lambda x: x[1] if x[1] == x[1] else -999, reverse=True)
    selected = [n for n, icir in ranked if icir is not None and icir > 0.3][:4]
    if len(selected) < 2:
        selected = [n for n, _ in ranked[:3]]

    print("Composite factors:", selected)
    combo = combine_factors(fdf, selected)
    ic = summarize_ic(factor_ic_series(combo, "score_combo"))
    print("Composite IC:", json.dumps(ic, indent=2))

    bt = run_long_only_backtest(
        combo,
        factor="score_combo",
        top_quantile=cfg.get("top_quantile", 0.2),
        cost_bps=cfg.get("transaction_cost_bps", 10),
    )
    stats = performance_stats(bt)
    print("Composite backtest:", json.dumps(stats, indent=2))

    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    bt.to_csv(out / "ashare_bt_combo.csv")
    print(f"Wrote {out / 'ashare_bt_combo.csv'}")


if __name__ == "__main__":
    main()
