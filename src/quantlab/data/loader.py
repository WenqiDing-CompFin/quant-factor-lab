"""Data loading facade — synthetic A-share / US now; real loaders later."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .synthetic_ashare import generate_ashare_panel
from .synthetic_us import generate_us_panel


def load_config(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_panel(config_path: str | Path | None = None, source: str = "synthetic") -> pd.DataFrame:
    """Load a research panel.

    Parameters
    ----------
    source : {'synthetic', 'csv'}
        'synthetic' — teaching demo with planted signals (market from config)
        'csv' — read market-specific sample CSV if present
    """
    cfg = load_config(config_path) if config_path else {}
    market = str(cfg.get("market", "ashare")).lower()

    if source == "csv":
        csv_name = "panel_us.csv" if market in {"us", "usa", "us_equity"} else "panel.csv"
        csv_path = Path("data/sample") / csv_name
        if not csv_path.exists():
            raise FileNotFoundError(
                f"{csv_path} not found. Run the matching build_demo_data script first."
            )
        return pd.read_csv(csv_path, parse_dates=["date"])

    if market in {"us", "usa", "us_equity"}:
        return generate_us_panel(
            start_date=cfg.get("start_date", "2015-01-01"),
            end_date=cfg.get("end_date", "2023-12-31"),
            n_stocks=int(cfg.get("n_stocks", 60)),
            seed=int(cfg.get("seed", 7)),
        )

    return generate_ashare_panel(
        start_date=cfg.get("start_date", "2018-01-01"),
        end_date=cfg.get("end_date", "2023-12-31"),
        n_stocks=int(cfg.get("n_stocks", 80)),
        seed=int(cfg.get("seed", 42)),
    )
