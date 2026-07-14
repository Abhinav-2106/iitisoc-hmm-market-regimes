import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from strategies import momentum, mean_reversion, cash

MOMENTUM_STATES       = {0, 4, 5}
MEAN_REVERSION_STATES = {2}
CASH_STATES           = {1, 3}

STATE_NAMES = {
    0: "Normal Bull",
    1: "Correction",
    2: "Neutral/Recovery",
    3: "Crisis/Panic",
    4: "Aggressive Bull",
    5: "Calm Bull",
}

def compute_signal(row: pd.Series) -> float:
    total = 0.0
    for i in range(6):
        prob = float(row[f"Forecast_State_{i}"])
        if i in MOMENTUM_STATES:
            s = momentum.signal(row["Close"], row["SMA50"])
        elif i in MEAN_REVERSION_STATES:
            s = mean_reversion.signal(row["RSI14"])
        else:
            s = cash.signal()
        total += prob * s
    return total


if __name__ == "__main__":

    path     = os.path.realpath("strategy_engine_3.py")
    data_dir = os.path.dirname(
        os.path.dirname(path)
    ).replace("src", "data")
    os.chdir(data_dir)

    prices_df = pd.read_csv("clean_data.csv")
    prices_df["Date"] = pd.to_datetime(prices_df["Date"])
    prices_df = prices_df.sort_values("Date").reset_index(drop=True)

    prices_df["SMA50"] = momentum.compute_sma(prices_df["Close"])
    prices_df["RSI14"] = mean_reversion.compute_rsi(prices_df["Close"])

    forecast_df = pd.read_csv("forecast_probabilities.csv")
    forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])
    forecast_df = forecast_df.sort_values("Date").reset_index(drop=True)

    df = forecast_df.merge(
        prices_df[["Date", "Close", "SMA50", "RSI14"]],
        on="Date",
        how="inner"
    )

    forecast_cols          = [f"Forecast_State_{i}" for i in range(6)]
    df["Forecasted_State"] = df[forecast_cols].values.argmax(axis=1)
    df["Forecast_Prob"]    = df[forecast_cols].max(axis=1)

    df["Target_Position"] = df.apply(compute_signal, axis=1)

    df["Trade_Size"] = (
        df["Target_Position"] - df["Target_Position"].shift(1)
    ).fillna(df["Target_Position"])

    output = df[["Date", "Target_Position", "Trade_Size"]]
    output.to_csv("signals_strategy_3.csv", index=False)

    print("signals_strategy_3.csv saved\n")

    print("Forecasted State Distribution:")
    dist = df["Forecasted_State"].value_counts().sort_index()
    for s, count in dist.items():
        pct = 100 * count / len(df)
        print(f"  State {s} ({STATE_NAMES[s]}): {count:4d} days  ({pct:.1f}%)")

    print("\nAverage Target Position by Forecasted State:")
    avg = df.groupby("Forecasted_State")["Target_Position"].mean()
    for s, pos in avg.items():
        print(f"  State {s} ({STATE_NAMES[s]}): {pos:.4f}")