import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .backtest import simulate
from .charts import report_charts


def main():
    p = argparse.ArgumentParser(description="Run a daily EMA/RSI/ATR strategy experiment")
    p.add_argument("--ticker", default="QQQ")
    p.add_argument("--start", default="2021-01-01")
    p.add_argument("--end", default="2026-01-01", help="Exclusive end date for downloads")
    p.add_argument("--csv", type=Path, help="Use a saved Date/High/Low/Close CSV")
    p.add_argument("--cost", type=float, default=0.001)
    p.add_argument("--output", type=Path, default=Path("results"))
    args = p.parse_args()
    try:
        if args.csv:
            prices = pd.read_csv(args.csv, index_col="Date", parse_dates=True)
        else:
            import yfinance as yf
            warmup = (pd.Timestamp(args.start)-pd.Timedelta(days=550)).strftime("%Y-%m-%d")
            prices = yf.Ticker(args.ticker).history(start=warmup, end=args.end, auto_adjust=True)
            if prices.empty:
                raise ValueError("No prices returned; check symbol, dates, and network")
            prices.index = prices.index.tz_localize(None)
        prices = prices.loc[prices.index < pd.Timestamp(args.end)]
        frame, metrics = simulate(prices, args.start, args.cost)
    except (ValueError, OSError) as exc:
        p.exit(1, f"Backtest failed: {exc}\n")
    args.output.mkdir(parents=True, exist_ok=True)
    prices.to_csv(args.output/"prices.csv", index_label="Date")
    frame.to_csv(args.output/"backtest.csv", index_label="Date")
    report = {"configuration": {"ticker": args.ticker, "start": args.start, "end_exclusive": args.end,
              "cost_per_unit_turnover": args.cost, "source": str(args.csv) if args.csv else "yfinance adjusted daily prices",
              "execution": "two-bar signal lag, close-to-close approximation; starts in cash"},
              "observed_start": str(frame.index[0].date()), "observed_end": str(frame.index[-1].date()),
              "metrics": metrics}
    (args.output/"summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for name, label in (("strategy", "Strategy"), ("benchmark", "Buy and hold")):
        axes[0].plot(frame.index, frame[f"{name}_equity"], label=label)
        axes[1].plot(frame.index, frame[f"{name}_drawdown"]*100, label=label)
    axes[0].set(ylabel="Growth of $1", title=f"{args.ticker}: daily strategy research")
    axes[1].set(ylabel="Drawdown (%)")
    for ax in axes:
        ax.legend(); ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(args.output/"performance.png", dpi=160); plt.close(fig)
    report_charts(frame, args.output, args.ticker)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

