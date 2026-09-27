"""Tests that the showcase remains descriptive rather than executable."""

from __future__ import annotations

import unittest

from public_framework import ResearchPipeline, StrategyNotIncludedError


class PublicBoundaryTest(unittest.TestCase):
    def test_disclosed_spec_is_stable(self) -> None:
        pipeline = ResearchPipeline.from_public_spec()

        self.assertEqual(pipeline.spec.horizon, "24h")
        self.assertEqual(pipeline.spec.bar_frequency, "15min")
        self.assertEqual(pipeline.spec.validation, "purged-walk-forward")
        self.assertEqual(pipeline.spec.universe_size, 355)

    def test_strategy_cannot_be_executed(self) -> None:
        pipeline = ResearchPipeline.from_public_spec()

        with self.assertRaises(StrategyNotIncludedError):
            pipeline.build_target_weights(market_panel=None)


if __name__ == "__main__":
    unittest.main()
