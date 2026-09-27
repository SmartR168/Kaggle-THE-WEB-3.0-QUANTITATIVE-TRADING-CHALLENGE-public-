# Methodology note

This document records the public XGBoost research protocol and the boundary around the confidential trading strategy. The feature and validation code is published; competition data, fitted artifacts, portfolio rules, and execution parameters are not.

## Research question

Can a cross-sectional machine-learning signal improve the selection of crypto perpetual futures while a separate, regime-aware trend and risk layer controls how that signal becomes exposure?

The project separates the question into four modules:

1. **Relative-return forecasting** — rank instruments by their 24-hour forward return.
2. **Regime measurement** — estimate trend direction and persistence at several horizons.
3. **Portfolio translation** — turn forecasts and regimes into volatility-scaled exposure.
4. **Conditional overlay** — deploy a grid only when the slower state supports it.

This separation makes ablation possible and reduces the temptation to credit every improvement to the predictor.

## Data and prediction task

- Market: crypto perpetual futures.
- Candidate universe: up to 355 contracts.
- Sampling interval: 15 minutes.
- Forecast horizon: 24 hours.
- Feature families: price momentum, realized volatility, liquidity, and technical state.
- Evaluation family: cross-sectional rank correlation with extra importance on the tails.

The disclosed reconstruction implements 1-day and 7-day momentum, 7-day realized volatility, 7-day log amount, RSI, normalized MACD, Bollinger z-score, and Amihud illiquidity. Feature construction accepts no target input, which makes accidental label-derived features harder to introduce. Listing rules and the original historical notebooks remain private.

## Validation protocol

### Purged walk-forward splits

The target spans multiple bars, so adjacent samples can share future-return information. A naïve random split would leak this overlap. The evaluation instead advances chronologically and purges observations around the train/validation boundary that conflict with the label horizon.

For every fold:

1. construct training data using information available at that time;
2. fit preprocessing and select features on the training slice only;
3. train the ranker;
4. score the next validation window;
5. store predictions before advancing the clock.

The public entry point exposes the fold lengths as command-line settings and publishes the historical core XGBoost configuration. Users remain responsible for choosing a defensible research window and for avoiding tuning on held-out folds.

### Evaluation hierarchy

The research distinguishes three levels of evidence:

- **model level:** cross-sectional rank quality and stability;
- **portfolio level:** risk-adjusted return after costs and funding;
- **component level:** ablation of the grid overlay against the EWMAC-only core.

This avoids selecting a model solely because one realized equity path looked attractive.

## Signal and portfolio layers

### Cross-sectional ranker

An XGBoost model captures nonlinear interactions across momentum, volatility, liquidity, and technical-state features. Its output is used as a relative score rather than a calibrated return forecast.

### EWMAC trend core

The trend state combines three exponentially weighted moving-average crossover pairs: 8/32, 16/64, and 32/128. After normalization, their direction and agreement determine a continuous core-exposure state. Volatility scaling controls the amount of risk assigned to that state.

### Dynamic-grid overlay

The overlay is active only in an eligible regime. Eligibility requires broad trend agreement and no material trend deterioration. Its spacing reacts to volatility so that the same nominal price move does not carry the same meaning in calm and stressed markets.

The private implementation contains additional safeguards. Publishing the trigger equations, spacing schedule, inventory rules, and unwind logic would make the strategy substantially reproducible, so those details are withheld.

## Costs and risk

The confidential trading engine produced the historical backtest summarized in the README and may account for funding, transaction fees, slippage, and portfolio constraints. Those components, the underlying return series, and the execution logic are not part of the disclosed XGBoost prediction code. The figure should therefore be read as an author-reported private backtest summary, not as a benchmark that can be independently regenerated from this repository.

## What would falsify the thesis

The research thesis would be weakened by any of the following:

- rank performance concentrated in a small number of folds;
- gains disappearing under plausible cost stress;
- the overlay improving return only by taking materially more tail risk;
- instability across liquidity or volatility regimes;
- feature selection drifting toward unavailable or revised information.

These tests belong in the private audit trail. Their presence in the methodology is not a claim that every possible robustness test has been passed.
