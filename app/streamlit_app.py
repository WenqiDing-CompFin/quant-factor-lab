"""Compatibility entrypoint for the unified cross-market dashboard."""

from pathlib import Path
from runpy import run_path

run_path(str(Path(__file__).resolve().parents[1] / "streamlit_app.py"), run_name="__main__")
