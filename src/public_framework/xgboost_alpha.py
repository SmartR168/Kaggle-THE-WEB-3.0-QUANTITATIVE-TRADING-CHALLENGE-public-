"""XGBoost cross-sectional alpha training with purged walk-forward evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .metrics import mean_cross_sectional_score
from .validation import walk_forward_splits


TARGET = "target_return_24h"
NON_FEATURE_COLUMNS = {"symbol", TARGET, "prediction", "fold"}


@dataclass(frozen=True, slots=True)
class XGBoostConfig:
    """Disclosed configuration from the historical XGBoost research track."""

    n_estimators: int = 1_000
    max_depth: int = 8
    learning_rate: float = 0.1
    subsample: float = 1.0
    random_state: int = 42
    n_jobs: int = -1


def _xgb_regressor(config: XGBoostConfig) -> Any:
    try:
        from xgboost import XGBRegressor
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Install the model extra first: pip install -e '.[model]'"
        ) from exc
    return XGBRegressor(
        objective="reg:squarederror",
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        learning_rate=config.learning_rate,
        subsample=config.subsample,
        random_state=config.random_state,
        n_jobs=config.n_jobs,
        tree_method="hist",
    )


def feature_columns(panel: pd.DataFrame) -> list[str]:
    """Return numeric model inputs while excluding identifiers and labels."""

    return [
        column
        for column in panel.columns
        if column not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(panel[column])
    ]


def fit_predict_walk_forward(
    panel: pd.DataFrame,
    *,
    min_train_timestamps: int,
    test_timestamps: int,
    purge_timestamps: int = 96,
    config: XGBoostConfig | None = None,
) -> tuple[pd.DataFrame, list[dict[str, float | int]]]:
    """Fit expanding XGBoost folds and return strictly out-of-sample scores.

    ``panel`` must use timestamps as its index and contain one row per
    timestamp/symbol pair. The purge is expressed in unique timestamps so a
    24-hour target on 15-minute bars uses at least 96 timestamps.
    """

    if TARGET not in panel:
        raise ValueError(f"panel must contain {TARGET!r}")
    if "symbol" not in panel:
        raise ValueError("panel must contain 'symbol'")
    if not isinstance(panel.index, pd.DatetimeIndex):
        raise TypeError("panel index must be a DatetimeIndex")

    cfg = config or XGBoostConfig()
    ordered = panel.sort_index().copy()
    timestamps = ordered.index.unique().sort_values()
    columns = feature_columns(ordered)
    if not columns:
        raise ValueError("panel has no numeric feature columns")

    fold_predictions: list[pd.DataFrame] = []
    diagnostics: list[dict[str, float | int]] = []
    splits = walk_forward_splits(
        len(timestamps),
        min_train_size=min_train_timestamps,
        test_size=test_timestamps,
        purge_size=purge_timestamps,
    )
    for fold, (train_positions, test_positions) in enumerate(splits, start=1):
        train_times = timestamps[train_positions]
        test_times = timestamps[test_positions]
        train = ordered.loc[ordered.index.isin(train_times)].dropna(subset=columns + [TARGET])
        test = ordered.loc[ordered.index.isin(test_times)].dropna(subset=columns + [TARGET])
        if train.empty or test.empty:
            continue

        model = _xgb_regressor(cfg)
        model.fit(train[columns], train[TARGET])
        prediction = test[["symbol", TARGET]].copy()
        prediction["prediction"] = np.asarray(model.predict(test[columns]), dtype=float)
        prediction["fold"] = fold
        score = mean_cross_sectional_score(prediction)
        fold_predictions.append(prediction)
        diagnostics.append(
            {
                "fold": fold,
                "train_rows": len(train),
                "test_rows": len(test),
                "weighted_spearman": score,
            }
        )

    if not fold_predictions:
        raise ValueError("no walk-forward fold produced predictions")
    return pd.concat(fold_predictions).sort_index(), diagnostics
