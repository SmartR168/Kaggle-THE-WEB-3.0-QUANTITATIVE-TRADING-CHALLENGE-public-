"""Public interfaces for the confidential research showcase."""

from .contracts import BacktestSummary, PublicResearchSpec
from .features import FeatureConfig, build_causal_features, build_forward_target
from .metrics import weighted_spearman
from .pipeline import ResearchPipeline, StrategyNotIncludedError
from .xgboost_alpha import XGBoostConfig, fit_predict_walk_forward

__all__ = [
    "BacktestSummary",
    "FeatureConfig",
    "PublicResearchSpec",
    "ResearchPipeline",
    "StrategyNotIncludedError",
    "XGBoostConfig",
    "build_causal_features",
    "build_forward_target",
    "fit_predict_walk_forward",
    "weighted_spearman",
]
