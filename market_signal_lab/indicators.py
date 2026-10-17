import pandas as pd


def indicators(prices):
    df = prices.copy()
    for span in (50, 200):
        df[f"ema{span}"] = df.Close.ewm(span=span, adjust=False, min_periods=span).mean()
    delta = df.Close.diff()
    up = delta.clip(lower=0).ewm(alpha=1/3, adjust=False, min_periods=3).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1/3, adjust=False, min_periods=3).mean()
    df["rsi"] = 100 - 100 / (1 + up / down)
    df.loc[(up == 0) & (down == 0), "rsi"] = 50
    tr = pd.concat([df.High-df.Low, (df.High-df.Close.shift()).abs(),
                    (df.Low-df.Close.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()
    df["vol_ratio"] = (df.atr/df.Close) / (df.atr/df.Close).rolling(100).mean()
    df["high20"] = df.High.rolling(20).max()
    return df
