"""Lesson entrypoint: list factors → compute → IC → layers → simple backtest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantlab.backtest import performance_stats, run_long_only_backtest
from quantlab.data.loader import load_config, load_panel
from quantlab.factors import FACTOR_CATALOG, compute_factors, list_factors
from quantlab.research import factor_ic_series, layer_returns, summarize_ic


def main() -> None:
    cfg = load_config(ROOT / "configs" / "ashare_demo.yaml")
    panel = load_panel(ROOT / "configs" / "ashare_demo.yaml", source="synthetic")
    names = cfg["factors"]

    print("=" * 60)
    print("STEP 0 — Factor catalog (selection starts with a story)")
    print("=" * 60)
    for spec in list_factors():
        if spec.name in names:
            print(f"[{spec.category:10}] {spec.name:16} dir={spec.direction:+d}  {spec.description_zh}")

    fdf = compute_factors(panel, factor_names=names)

    print("\n" + "=" * 60)
    print("STEP 1 — Single-factor Rank IC")
    print("=" * 60)
    rows = []
    for name in names:
        ic = factor_ic_series(fdf, name)
        summary = summarize_ic(ic)
        summary["factor"] = name
        summary["category"] = FACTOR_CATALOG[name].category
        rows.append(summary)
        print(
            f"{name:16} meanIC={summary['mean_ic']:+.4f}  "
            f"ICIR={summary['icir']:+.3f}  t={summary['t_stat']:+.2f}  "
            f"pos%={summary['pos_ratio']:.1%}"
        )

    ic_table = pd.DataFrame(rows).sort_values("icir", ascending=False)
    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    ic_table.to_csv(out_dir / "ashare_ic_summary.csv", index=False)

    print("\n" + "=" * 60)
    print("STEP 2 — Keep factors with ICIR > 0.3 (teaching rule of thumb)")
    print("=" * 60)
    keep = ic_table.loc[ic_table["icir"] > 0.3, "factor"].tolist()
    print("Selected:", keep if keep else "(none — still demo backtest on best ICIR)")
    if not keep:
        keep = [ic_table.iloc[0]["factor"]]

    best = keep[0]
    layered = layer_returns(fdf, best, n_layers=cfg.get("n_layers", 5))
    print(f"\nLayer mean returns for {best}:")
    print(layered.mean().to_string())

    bt = run_long_only_backtest(
        fdf,
        factor=best,
        top_quantile=cfg.get("top_quantile", 0.2),
        cost_bps=cfg.get("transaction_cost_bps", 10),
    )
    stats = performance_stats(bt)
    print(f"\nLong-only backtest on {best}:")
    print(json.dumps(stats, indent=2))
    bt.to_csv(out_dir / f"ashare_bt_{best}.csv")
    print(f"\nArtifacts → {out_dir}")


if __name__ == "__main__":
    main()
