import numpy as np

from .indicators import indicators


def simulate(prices, start, cost=0.001):
    """Daily close-to-close approximation; signals take effect one full bar later."""
    required = {"Close", "High", "Low"}
    if not required.issubset(prices.columns):
        raise ValueError("CSV must contain Close, High, Low columns")
    if not prices.index.is_monotonic_increasing or prices.index.has_duplicates:
        raise ValueError("Dates must be sorted and unique")
    if len(prices) < 201 or not np.isfinite(prices[list(required)]).all().all():
        raise ValueError("Need at least 201 finite price rows")
    if (prices[list(required)] <= 0).any().any() or cost < 0 or cost >= 1:
        raise ValueError("Prices must be positive and cost must be in [0, 1)")
    df = indicators(prices)
    buy = (df.Close > df.ema200) & ((df.rsi < 30) | (df.Close < df.high20-1.5*df.atr))
    target = np.where(buy, np.where(df.vol_ratio > 1.2, 0.5, 1.0), np.nan)
    target = np.where(df.Close < df.ema50, 0.0, target)
    df["target"] = target
    df = df.loc[start:].copy()
    if len(df) < 2 or df.ema200.isna().any():
        raise ValueError("Need 200 warm-up bars before the evaluation period and 2 evaluation bars")
    # Evaluation starts in cash. Bar t signal first earns the return of bar t+2.
    df["position"] = df.target.ffill().fillna(0).shift(2).fillna(0)
    df["turnover"] = df.position.diff().fillna(df.position).abs()
    df["market_return"] = df.Close.pct_change().fillna(0)
    df["strategy_return"] = df.position*df.market_return - df.turnover*cost
    df["benchmark_return"] = df.market_return
    df.iloc[0, df.columns.get_loc("benchmark_return")] = -cost
    for name in ("strategy", "benchmark"):
        df[f"{name}_equity"] = (1+df[f"{name}_return"]).cumprod()
        peak = df[f"{name}_equity"].cummax().clip(lower=1)
        df[f"{name}_drawdown"] = df[f"{name}_equity"]/peak-1
    metrics = {name: {"total_return": float(df[f"{name}_equity"].iloc[-1]-1),
                       "max_drawdown": float(df[f"{name}_drawdown"].min())}
               for name in ("strategy", "benchmark")}
    metrics["strategy"]["one_way_turnover"] = float(df.turnover.sum())
    return df, metrics
