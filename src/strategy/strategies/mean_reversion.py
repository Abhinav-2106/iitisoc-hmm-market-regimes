import pandas as pd
import numpy as np


RSI_WINDOW = 14
BB_WINDOW = 20
BB_STD = 2.0


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds all indicators required by the
    mean reversion strategy.

    Returns a new DataFrame.
    """

    df = df.copy()

    # RSI 

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        com=RSI_WINDOW - 1,
        min_periods=RSI_WINDOW
    ).mean()

    avg_loss = loss.ewm(
        com=RSI_WINDOW - 1,
        min_periods=RSI_WINDOW
    ).mean()

    rs = avg_gain / avg_loss

    df["RSI14"] = (100 -(100/(1 + rs)))
    
    # BB

    df["BB_Middle"] = (
        df["Close"]
        .rolling(BB_WINDOW)
        .mean()
    )

    rolling_std = (
        df["Close"]
        .rolling(BB_WINDOW)
        .std()
    )

    df["BB_Upper"] = (
        df["BB_Middle"]
        +
        BB_STD * rolling_std
    )

    df["BB_Lower"] = (
        df["BB_Middle"]
        -
        BB_STD * rolling_std
    )

    return df


    
def score(close : float, rsi: float, bb_upper : float, bb_lower : float) -> float:
    """
    Computes a continuous mean reversion confidence score.

    Components:
    - RSI
    - Bollinger Band position

    Returns:
        float in [0,1]

    1.0 -> Strong mean reversion opportunity
    0.5 -> Neutral
    0.0 -> Strong overbought
    """

    if (pd.isna(rsi) or pd.isna(bb_upper) or pd.isna(bb_lower)):
        return 0.5
    

    bb_width = bb_upper - bb_lower

    if bb_width <= 0:
        bb_score = 0.5
    else:
        bb_score = (1.0  -( (close - bb_lower)/bb_width))

        bb_score = float(np.clip(bb_score,0.0,1.0))

    
    
    rsi_score = float(np.clip(1.0 - rsi / 100,0.0,1.0))

    # experimenting
    base_score = (
        0.5 * bb_score
        +
        0.5 * rsi_score
    )

    oversold = (
        rsi < 30
        and
        close < bb_lower
    )

    overbought = (
        rsi > 70
        and
        close > bb_upper
    )

    if oversold:

        base_score = min(
            base_score + 0.10,
            1.0
        )

    elif overbought:

        base_score = max(
            base_score - 0.10,
            0.0
        )

    return float(base_score)