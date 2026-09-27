"""Causal XGBoost feature construction separated from forward-looking labels."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureConfig:
    bars_per_day: int = 96
    momentum_days: int = 7
    volatility_days: int = 7
    amount_days: int = 7
    prediction_horizon_days: int = 1

    @property
    def horizon_bars(self) -> int:
        return self.bars_per_day * self.prediction_horizon_days


def _rsi(price: pd.Series, window: int) -> pd.Series:
    change = price.diff()
    gain = change.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    loss = (-change.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    relative_strength = gain / loss.replace(0, np.nan)
    return 100.0 - 100.0 / (1.0 + relative_strength)


def build_causal_features(
    frame: pd.DataFrame, config: FeatureConfig | None = None
) -> pd.DataFrame:
    """Build features available at or before each timestamp.

    The target is intentionally not accepted by this function. Keeping feature
    and label construction separate makes accidental target leakage harder.
    """

    cfg = config or FeatureConfig()
    if not frame.index.is_monotonic_increasing:
        frame = frame.sort_index()
    required = {"vwap", "amount"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing feature inputs: {sorted(missing)}")

    price = pd.to_numeric(frame["vwap"], errors="coerce")
    amount = pd.to_numeric(frame["amount"], errors="coerce")
    returns = price.pct_change(fill_method=None)
    seven_day = cfg.bars_per_day * cfg.momentum_days
    vol_window = cfg.bars_per_day * cfg.volatility_days
    amount_window = cfg.bars_per_day * cfg.amount_days

    fast_ema = price.ewm(span=12 * cfg.bars_per_day, adjust=False).mean()
    slow_ema = price.ewm(span=26 * cfg.bars_per_day, adjust=False).mean()
    rolling_mean = price.rolling(seven_day, min_periods=seven_day).mean()
    rolling_std = price.rolling(seven_day, min_periods=seven_day).std()

    features = pd.DataFrame(index=frame.index)
    features["momentum_1d"] = price.pct_change(cfg.bars_per_day, fill_method=None)
    features["momentum_7d"] = price.pct_change(seven_day, fill_method=None)
    features["volatility_7d"] = returns.rolling(vol_window, min_periods=vol_window).std()
    features["log_amount_7d"] = np.log1p(
        amount.rolling(amount_window, min_periods=amount_window).sum()
    )
    features["rsi_7d"] = _rsi(price, seven_day)
    features["macd"] = (fast_ema - slow_ema) / price.replace(0, np.nan)
    features["bollinger_z"] = (price - rolling_mean) / rolling_std.replace(0, np.nan)
    features["amihud_7d"] = (returns.abs() / amount.replace(0, np.nan)).rolling(
        vol_window, min_periods=vol_window
    ).mean()
    return features.replace([np.inf, -np.inf], np.nan)


def build_forward_target(
    frame: pd.DataFrame, config: FeatureConfig | None = None
) -> pd.Series:
    """Compute the 24-hour forward VWAP return used as the research label."""

    cfg = config or FeatureConfig()
    price = pd.to_numeric(frame["vwap"], errors="coerce")
    target = price.shift(-cfg.horizon_bars) / price - 1.0
    target.name = "target_return_24h"
    return target


def make_supervised_frame(
    frame: pd.DataFrame, symbol: str, config: FeatureConfig | None = None
) -> pd.DataFrame:
    """Combine causal features and the label for one symbol."""

    cfg = config or FeatureConfig()
    features = build_causal_features(frame, cfg)
    target = build_forward_target(frame, cfg)
    result = features.join(target).dropna()
    result.insert(0, "symbol", symbol)
    return result
