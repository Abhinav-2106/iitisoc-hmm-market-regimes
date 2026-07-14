import pandas as pd

SMA_WINDOW = 50


def compute_sma(prices: pd.Series, window: int = SMA_WINDOW) -> pd.Series:
    return prices.rolling(window=window).mean()


def signal(close: float, sma: float) -> float:
    """
    Long  (1.0) : Close is above SMA50 — uptrend intact.
    Cash  (0.0) : Close is below SMA50 — trend broken.
    """
    return 1.0 if close > sma else 0.0