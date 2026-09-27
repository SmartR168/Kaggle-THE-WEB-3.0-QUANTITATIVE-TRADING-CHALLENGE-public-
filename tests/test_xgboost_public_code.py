"""Regression tests migrated with the disclosed XGBoost research code."""

from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from public_framework.features import FeatureConfig, build_causal_features, build_forward_target
from public_framework.metrics import weighted_spearman
from public_framework.validation import walk_forward_splits


def sample_frame(n: int = 50) -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC")
    price = pd.Series(np.linspace(100.0, 150.0, n), index=index)
    return pd.DataFrame({"vwap": price, "amount": 1_000.0}, index=index)


class XGBoostPublicCodeTest(unittest.TestCase):
    def test_forward_target_uses_future_horizon(self) -> None:
        frame = sample_frame()
        config = FeatureConfig(bars_per_day=4, prediction_horizon_days=1)
        target = build_forward_target(frame, config)
        expected = frame["vwap"].iloc[4] / frame["vwap"].iloc[0] - 1.0
        self.assertTrue(np.isclose(target.iloc[0], expected))
        self.assertTrue(target.iloc[-4:].isna().all())

    def test_features_do_not_change_when_future_is_modified(self) -> None:
        frame = sample_frame()
        config = FeatureConfig(
            bars_per_day=2,
            momentum_days=2,
            volatility_days=2,
            amount_days=2,
        )
        original = build_causal_features(frame, config)
        changed = frame.copy()
        changed.iloc[-1, changed.columns.get_loc("vwap")] = 1_000_000.0
        recomputed = build_causal_features(changed, config)
        pd.testing.assert_series_equal(original.iloc[-2], recomputed.iloc[-2])

    def test_weighted_spearman_perfect_and_reverse(self) -> None:
        truth = np.array([3.0, 1.0, 4.0, 2.0])
        self.assertTrue(math.isclose(weighted_spearman(truth, truth), 1.0))
        self.assertTrue(math.isclose(weighted_spearman(truth, -truth), -1.0))

    def test_walk_forward_split_has_purge(self) -> None:
        train, test = next(
            walk_forward_splits(
                40,
                min_train_size=10,
                test_size=5,
                purge_size=3,
            )
        )
        self.assertTrue(np.array_equal(train, np.arange(10)))
        self.assertTrue(np.array_equal(test, np.arange(13, 18)))
        self.assertEqual(test.min() - train.max() - 1, 3)


if __name__ == "__main__":
    unittest.main()
