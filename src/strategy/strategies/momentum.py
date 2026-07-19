import pandas as pd

sma_fast = 20
sma_slow = 50

def compute_indicators(df: pd.dataframe) -> pd.dataframe:
    """
    compute all indicators required by the momentum strategy.
    """

    df = df.copy()

    df["SMA20"] = df["Close"].rolling(sma_fast).mean()
    df["SMA50"] = df["Close"].rolling(sma_slow).mean()
    
    return df


def score(close : float, sma20 : float, sma50 : float) -> float:
    """
    computes a continuous momentum confidence score.

    weights:
    - 0.50 : close > sma50
    - 0.30 : sma20 > sma50
    - 0.20 : close > sma20

    returns:
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