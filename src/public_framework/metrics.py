"""Competition ranking and portfolio metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_spearman(
    y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray
) -> float:
    """Return the competition's tail-weighted Spearman rank correlation."""

    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if true.shape != pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")

    valid = np.isfinite(true) & np.isfinite(pred)
    true = true[valid]
    pred = pred[valid]
    if true.size < 2:
        return float("nan")

    true_rank = pd.Series(true).rank(ascending=False, method="average").to_numpy()
    pred_rank = pd.Series(pred).rank(ascending=False, method="average").to_numpy()
    normalized_rank = 2.0 * (true_rank - 1.0) / (true.size - 1.0) - 1.0
    weights = normalized_rank**2

    weight_sum = weights.sum()
    true_mean = np.dot(weights, true_rank) / weight_sum
    pred_mean = np.dot(weights, pred_rank) / weight_sum
    true_centered = true_rank - true_mean
    pred_centered = pred_rank - pred_mean
    denominator = np.sqrt(
        np.dot(weights, true_centered**2) * np.dot(weights, pred_centered**2)
    )
    if denominator == 0:
        return float("nan")
    return float(np.dot(weights, true_centered * pred_centered) / denominator)


def mean_cross_sectional_score(predictions: pd.DataFrame) -> float:
    """Average the competition score across timestamps."""

    required = {"target_return_24h", "prediction"}
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"Missing prediction columns: {sorted(missing)}")
    scores = predictions.groupby(level=0, sort=True).apply(
        lambda group: weighted_spearman(
            group["target_return_24h"], group["prediction"]
        ),
        include_groups=False,
    )
    return float(scores.mean())
