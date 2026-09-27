"""Loading helpers for the competition's per-symbol Parquet files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PRICE_COLUMNS = ("open_price", "high_price", "low_price", "close_price")
NUMERIC_COLUMNS = PRICE_COLUMNS + ("volume", "amount", "buy_volume", "buy_amount")


def discover_symbols(data_dir: str | Path) -> list[str]:
    """Return sorted symbol names discovered in a raw data directory."""

    directory = Path(data_dir)
    if not directory.is_dir():
        raise FileNotFoundError(f"Data directory not found: {directory}")
    return sorted(path.stem for path in directory.glob("*.parquet"))


def load_symbol(path: str | Path) -> pd.DataFrame:
    """Load one symbol, normalize types, and add a VWAP column."""

    source = Path(path)
    frame = pd.read_parquet(source)
    required = {"timestamp", "close_price", "volume", "amount"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{source.name} is missing columns: {sorted(missing)}")

    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
    for column in NUMERIC_COLUMNS:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    frame = frame.set_index("timestamp")
    frame["vwap"] = (frame["amount"] / frame["volume"]).replace([np.inf, -np.inf], np.nan)
    frame["vwap"] = frame["vwap"].ffill()
    return frame
