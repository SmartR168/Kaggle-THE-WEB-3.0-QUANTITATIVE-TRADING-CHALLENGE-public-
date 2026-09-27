# Results and disclosure

## Reported results

| Metric | Value | Provenance |
|:--|--:|:--|
| Competition rank | 14 / 128 | Author-supplied achieved result |
| Annualized return | 20.8% | Author-reported private historical backtest |
| Sharpe ratio | 1.27 | Author-reported private historical backtest |
| Maximum drawdown | 11.3% | Author-reported private historical backtest |
| Grid uplift: annualized return | +2.9 percentage points | Private historical ablation |
| Grid uplift: Sharpe | +0.08 | Private historical ablation |

The EWMAC-only comparison values—17.9% annualized return and 1.19 Sharpe—come from the corresponding private historical ablation. The combined strategy's reported improvement is measured against that private comparison run.

## What the chart means

`historical-backtest-results.png` presents the author's historical backtest output for the EWMAC-only core and the combined XGBoost, EWMAC, and Dynamic Grid strategy. The combined result reports 20.8% annualized return, a 1.27 Sharpe ratio, and approximately 11.3% maximum drawdown; the EWMAC-only comparison reports 17.9% annualized return and a 1.19 Sharpe ratio.

The underlying return series, trade ledger, market-data snapshot, parameter set, and confidential strategy engine are not published. As a result, the chart represents an author-reported private backtest result but cannot be independently reproduced or audited from this public repository alone.

## Verification status

The public XGBoost code is executable with authorized competition parquet files and can produce out-of-sample rank predictions. It does not implement the confidential EWMAC / Dynamic Grid trading strategy and cannot regenerate the published portfolio-performance chart.

The competition rank and portfolio results are both reported by the author. The repository exposes enough code to inspect the public prediction and validation framework, but not enough data or implementation detail to independently verify the private portfolio backtest.

## Confidentiality boundary

The following materials are intentionally absent:

- competition data and derived datasets;
- the historical portfolio-return series and trade ledger;
- trained models and serialized preprocessing objects;
- original historical notebooks and their local paths;
- portfolio weights and order-generation logic;
- grid thresholds, spacing, inventory, and exit logic;
- venue credentials, endpoints, and production infrastructure.

## Risk statement

The chart reports a historical backtest, not live trading performance, an exchange-account statement, or a guarantee of future results. Crypto perpetual futures involve leverage, liquidation, basis, funding, liquidity, counterparty, operational, and regulatory risks. Fees, slippage, and market impact can change materially across venues and regimes, and the withheld private inputs prevent independent assessment of every backtest assumption.

Past or simulated performance is not indicative of future results. Nothing in this repository is investment advice, a solicitation, or a promise of performance.
