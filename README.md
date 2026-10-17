# Market Signal Lab

Rule-based market strategy research with Python, historical backtesting, and a Discord alert prototype.

## Overview

This project explores a practical research question: how do trend filters, pullback entries, and volatility-aware exposure affect the tradeoff between return and drawdown?

The experimental notebook studies QQQ across intraday, hourly, and daily timeframes, with additional QQQ/TQQQ allocation experiments. It also includes a polling-based Discord alert prototype for VOO, QQQ, and TSLA.

This is an exploratory research project. It does not train a machine learning model or predict future prices, and it does not execute brokerage orders.

## Implemented experiments

- EMA trend filters using several lookback periods.
- RSI and ATR pullback entry rules.
- Strategy equity curves, total return, and maximum drawdown calculations.
- Comparisons against QQQ buy-and-hold.
- A volatility-ratio rule that selects 50% or 100% exposure on qualifying entries.
- A proportional transaction-cost approximation in the V12 experiment.
- A grid search over TQQQ allocations during periods outside the primary QQQ strategy.
- Discord webhook alerts with an in-memory per-symbol cooldown.

## Recorded findings

The original notebook contains exploratory results showing that several strategies reduced drawdown while also giving up substantial upside. This motivated experiments with entry thresholds, holding rules, and exposure sizing.

These are observations from the supplied notebook, not independently reproduced performance claims. The original runs use rolling date windows and do not save the underlying price snapshots or exact execution dates. A fresh download may produce different results.

## Project layout

```text
market-signal-lab/
  notebooks/
    strategy_experiments.ipynb
  requirements.txt
  .env.example
  .gitignore
  README.md
  PROJECT_DESCRIPTION.md
```

## Local setup

Use Python 3.10 or newer as a starting environment; compatibility has not yet been verified.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab notebooks/strategy_experiments.ipynb
```

Dependencies are currently unpinned. A tested lockfile is future work.

Run individual backtest experiments selectively. The first code cell starts a continuous polling loop when executed; interrupt it before moving to other cells. Some cells redefine functions, so run the imports and definitions belonging to the experiment you select.

Historical data is downloaded through yfinance and requires network access. Availability of intraday history depends on the provider.

### Optional Discord alerts

Set the environment variable before launching Jupyter:

```powershell
$env:DISCORD_WEBHOOK_URL = "your_webhook_url"
jupyter lab notebooks/strategy_experiments.ipynb
```

`.env.example` documents the variable only; this project does not automatically load `.env` files. The alert cell sends messages when its conditions are satisfied. Use a dedicated test channel.

## Research limitations

- Repeated parameter tuning uses overlapping historical windows; there is no held-out evaluation or walk-forward validation.
- Shifted positions provide a basic timing convention, but realistic next-open fills, spreads, and order execution are not modeled.
- Transaction costs are included only in a subset of experiments. Results across versions are not a controlled comparison.
- Indicator warm-up periods are not consistently excluded from evaluation.
- Mixed daily/intraday experiments require a separate timestamp-alignment and look-ahead-bias audit.
- The TQQQ allocation search assumes a constant annual cash rate and omits trading costs; it does not establish an optimal future allocation.
- Volatility-based exposure is a heuristic, not portfolio risk parity.
- Alert position sizing is based on stop distance and does not cap shares by available cash.
- The alert prototype uses temporary cooldown state, has limited delivery/error handling, and may process an unfinished price bar.
- Historical data and a reproducible execution environment are not bundled.

## Next steps

1. Separate indicators, strategy rules, evaluation, and alerts into modules.
2. Save dated input data and explicit experiment configurations.
3. Add consistent costs, execution assumptions, and warm-up handling.
4. Evaluate on held-out periods and additional symbols.
5. Add equity/drawdown charts and tests for position timing and accounting.
6. Make alerts optional, cash-constrained, and resilient to delivery failures.

## Publication notes

The notebook copy has had outputs cleared and the embedded Discord webhook replaced with an environment-variable lookup. Rotate the original webhook before publishing. If it was previously committed, removing it from the current file does not remove it from repository history.

The supplied notebook has been preserved as an experimental archive rather than presented as a production trading system. Code has not been executed or performance independently verified during this packaging pass.
