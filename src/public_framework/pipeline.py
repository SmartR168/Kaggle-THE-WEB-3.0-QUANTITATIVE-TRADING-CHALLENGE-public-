"""Non-runnable orchestration skeleton for the public research showcase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import PublicResearchSpec


class StrategyNotIncludedError(NotImplementedError):
    """Raised when public code reaches a confidential strategy boundary."""


@dataclass(frozen=True, slots=True)
class ResearchPipeline:
    """Documents component boundaries without releasing decision logic."""

    spec: PublicResearchSpec

    @classmethod
    def from_public_spec(
        cls,
        *,
        horizon: str = "24h",
        bar_frequency: str = "15min",
        validation: str = "purged-walk-forward",
    ) -> "ResearchPipeline":
        return cls(
            PublicResearchSpec(
                horizon=horizon,
                bar_frequency=bar_frequency,
                validation=validation,
            )
        )

    def build_target_weights(self, market_panel: Any) -> None:
        """Stop at the exact boundary where proprietary logic would begin."""

        del market_panel
        raise StrategyNotIncludedError(
            "Alpha features, fitted models, EWMAC normalization, grid triggers, "
            "and portfolio sizing are intentionally excluded from the public repository."
        )
