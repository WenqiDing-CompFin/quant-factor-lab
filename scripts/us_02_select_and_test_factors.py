"""US module: factor catalog → Rank IC → layers → long-only backtest."""

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
from quantlab.research import factor_corr_matrix, factor_ic_series, layer_returns, summarize_ic


def main() -> None:
    cfg = load_config(ROOT / "configs" / "us_demo.yaml")
    panel = load_panel(ROOT / "configs" / "us_demo.yaml", source="synthetic")
    names = cfg["factors"]

    print("=" * 60)
    print("US · STEP 0 — Factor catalog")
    print("=" * 60)
    for spec in list_factors():
        if spec.name in names:
            print(f"[{spec.category:10}] {spec.name:16} {spec.description_en}")

    fdf = compute_factors(panel, factor_names=names)

    print("\n" + "=" * 60)
    print("US · STEP 1 — Rank IC")
    print("=" * 60)
    rows = []
    for name in names:
        summary = summarize_ic(factor_ic_series(fdf, name))
        summary["factor"] = name
        summary["category"] = FACTOR_CATALOG[name].category
        rows.append(summary)
        print(
            f"{name:16} meanIC={summary['mean_ic']:+.4f}  "
            f"ICIR={summary['icir']:+.3f}  t={summary['t_stat']:+.2f}"
        )

    ic_table = pd.DataFrame(rows).sort_values("icir", ascending=False)
    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    ic_table.to_csv(out_dir / "us_ic_summary.csv", index=False)

    print("\n" + "=" * 60)
    print("US · STEP 2 — Keep ICIR > 0.3")
    print("=" * 60)
    keep = ic_table.loc[ic_table["icir"] > 0.3, "factor"].tolist()
    print("Selected:", keep)
    if not keep:
        keep = [ic_table.iloc[0]["factor"]]

    corr = factor_corr_matrix(fdf, keep)
    corr.to_csv(out_dir / "us_factor_corr.csv")
    print("\nAvg Spearman corr among selected:")
    print(corr.round(2).to_string())

    best = keep[0]
    layered = layer_returns(fdf, best, n_layers=cfg.get("n_layers", 5))
    print(f"\nLayer means for {best}:")
    print(layered.mean().to_string())

    bt = run_long_only_backtest(
        fdf,
        factor=best,
        top_quantile=cfg.get("top_quantile", 0.2),
        cost_bps=cfg.get("transaction_cost_bps", 5),
    )
    stats = performance_stats(bt)
    print(f"\nLong-only backtest on {best}:")
    print(json.dumps(stats, indent=2))
    bt.to_csv(out_dir / f"us_bt_{best}.csv")
    print(f"\nArtifacts → {out_dir}")


if __name__ == "__main__":
    main()
