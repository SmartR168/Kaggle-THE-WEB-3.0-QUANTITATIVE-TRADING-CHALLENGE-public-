"""Train the disclosed XGBoost ranker on local competition parquet files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from public_framework.data import discover_symbols, load_symbol
from public_framework.features import FeatureConfig, make_supervised_frame
from public_framework.xgboost_alpha import fit_predict_walk_forward


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Directory containing one parquet per symbol")
    parser.add_argument("--output", type=Path, default=Path("artifacts/xgboost_oos_predictions.csv"))
    parser.add_argument("--max-symbols", type=int, default=None)
    parser.add_argument("--min-train-days", type=int, default=90)
    parser.add_argument("--test-days", type=int, default=14)
    args = parser.parse_args()

    feature_config = FeatureConfig()
    symbols = discover_symbols(args.data_dir)[: args.max_symbols]
    panels = [
        make_supervised_frame(
            load_symbol(args.data_dir / f"{symbol}.parquet"), symbol, feature_config
        )
        for symbol in symbols
    ]
    panel = pd.concat(panels).sort_index()
    predictions, diagnostics = fit_predict_walk_forward(
        panel,
        min_train_timestamps=args.min_train_days * feature_config.bars_per_day,
        test_timestamps=args.test_days * feature_config.bars_per_day,
        purge_timestamps=feature_config.horizon_bars,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output)
    diagnostics_path = args.output.with_suffix(".folds.json")
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    print(f"wrote {args.output} and {diagnostics_path}")


if __name__ == "__main__":
    main()
