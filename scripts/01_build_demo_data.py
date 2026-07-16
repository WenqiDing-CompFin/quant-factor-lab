"""Build and cache the synthetic A-share demo panel."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantlab.data.loader import load_config, load_panel


def main() -> None:
    cfg_path = ROOT / "configs" / "ashare_demo.yaml"
    df = load_panel(cfg_path, source="synthetic")
    out = ROOT / "data" / "sample" / "panel.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows → {out}")
    print(df.head(3))


if __name__ == "__main__":
    main()
