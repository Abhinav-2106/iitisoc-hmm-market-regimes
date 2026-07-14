import pandas as pd

RSI_WINDOW     = 14
RSI_OVERSOLD   = 30
RSI_OVERBOUGHT = 70


def compute_rsi(prices: pd.Series, window: int = RSI_WINDOW) -> pd.Series:
    delta    = prices.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
    rs       = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def signal(rsi: float) -> float:
    """
    Oversold   RSI < 30  → Full long   (1.0)
    Overbought RSI > 70  → Flat / cash (0.0)
    Neutral    30-70     → Half pos    (0.5)
    """
    if rsi < RSI_OVERSOLD:
        return 1.0
    elif rsi > RSI_OVERBOUGHT:
        return 0.0
    else:
        return 0.5