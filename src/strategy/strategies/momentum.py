import pandas as pd

SMA_FAST = 20
SMA_SLOW = 50

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all indicators required by the momentum strategy.
    """

    df = df.copy()

    df["SMA20"] = df["Close"].rolling(SMA_FAST).mean()
    df["SMA50"] = df["Close"].rolling(SMA_SLOW).mean()
    
    return df


def score(close : float, sma20 : float, sma50 : float) -> float:
    """
    Computes a continuous momentum confidence score.

    Weights:
    - 0.50 : Close > SMA50
    - 0.30 : SMA20 > SMA50
    - 0.20 : Close > SMA20

    Returns:
        float in [0.0, 1.0]
    """

    score = 0.0

    if pd.isna(sma20) or pd.isna(sma50):
        return 0.0

    if close > sma50:
        score += 0.5
    
    if sma20 > sma50:
        score += 0.3
    
    if close > sma20:
        score += 0.2
    
    return score