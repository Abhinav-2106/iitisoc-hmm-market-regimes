def calculate_drawdown(equity):
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return drawdown

def calculate_rsi(close, period=14):
    change = close.diff()
    gain = change.where(change > 0, 0)
    loss = -change.where(change < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_rsi(df):
    df = df.copy()
    if "RSI" not in df.columns:
        df["RSI"] = calculate_rsi(df["Close"])
    return df
