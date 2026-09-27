"""Typed public contracts; no proprietary strategy implementation is included."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias


Timestamp: TypeAlias = str
Symbol: TypeAlias = str


@dataclass(frozen=True, slots=True)
class PublicResearchSpec:
    """High-level research settings that are safe to disclose."""

    horizon: str = "24h"
    bar_frequency: str = "15min"
    validation: str = "purged-walk-forward"
    universe_size: int = 355


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    """Aggregate result schema used by the private reporting layer."""

    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    includes_funding_fees_slippage: bool


class AlphaRanker(Protocol):
    """Maps a point-in-time feature row to a relative cross-sectional score."""

    def score(self, *, timestamp: Timestamp, symbol: Symbol) -> float: ...


class RegimeModel(Protocol):
    """Summarizes multi-horizon market state without exposing its parameters."""

    def state(self, *, timestamp: Timestamp, symbol: Symbol) -> float: ...


class PortfolioPolicy(Protocol):
    """Translates scores and regimes into target weights."""

    def target_weight(
        self,
        *,
        timestamp: Timestamp,
        symbol: Symbol,
        alpha_score: float,
        regime_state: float,
    ) -> float: ...


class CostModel(Protocol):
    """Estimates implementation friction for a proposed position change."""

    def estimate_bps(
        self,
        *,
        timestamp: Timestamp,
        symbol: Symbol,
        weight_change: float,
    ) -> float: ...
