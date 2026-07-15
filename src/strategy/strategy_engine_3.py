import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from strategies import momentum, mean_reversion, risk

print(risk.__file__)
print(dir(risk))

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

def aggregate_regimes(row: pd.Series):
    """
    Aggregate the six forecasted HMM states into
    Bull, Neutral and Bear probabilities.
    """

    bull_prob = (
        row["Forecast_State_0"]
        + row["Forecast_State_4"]
        + row["Forecast_State_5"]
    )

    neutral_prob = (
        row["Forecast_State_2"]
    )

    bear_prob = (
        row["Forecast_State_1"]
        + row["Forecast_State_3"]
    )

    return (
        bull_prob,
        neutral_prob,
        bear_prob,
    )

def compute_position_row(
    row: pd.Series,
    transition_matrix: np.ndarray,
) -> float:
    """
    Computes the final portfolio position for a single day.
    """

    # Aggregate forecast probabilities
    bull_prob, neutral_prob, bear_prob = aggregate_regimes(row)

    # Strategy confidence scores
    momentum_score = momentum.score(
        row["Close"],
        row["SMA20"],
        row["SMA50"],
    )

    mr_score = mean_reversion.score(
        row["Close"],
        row["RSI14"],
        row["BB_Upper"],
        row["BB_Lower"],
    )

    # Raw signals
    bull_signal = bull_prob * momentum_score
    neutral_signal = neutral_prob * mr_score

    # Forecast probability vector
    forecast_probs = np.array([
        row[f"Forecast_State_{i}"]
        for i in range(6)
    ])

    # Expected regime stability
    stability = risk.expected_stability(
        forecast_probs,
        transition_matrix,
    )

    # Apply risk management
    return risk.apply_risk(
        bull_signal,
        neutral_signal,
        stability,
    )

if __name__ == "__main__":

    # ------------------------------------------------------------
    # Resolve data directory
    # ------------------------------------------------------------
    path = os.path.realpath("strategy_engine_3_5.py")

    data_dir = os.path.dirname(
        os.path.dirname(path)
    ).replace("src", "data")

    os.chdir(data_dir)

    # ------------------------------------------------------------
    # Load price data
    # ------------------------------------------------------------
    prices_df = pd.read_csv("clean_data.csv")

    prices_df["Date"] = pd.to_datetime(
        prices_df["Date"]
    )

    prices_df = (
        prices_df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # Compute strategy indicators
    # ------------------------------------------------------------
    prices_df = momentum.compute_indicators(prices_df)

    prices_df = mean_reversion.compute_indicators(prices_df)

    # ------------------------------------------------------------
    # Load forecast probabilities
    # ------------------------------------------------------------
    forecast_df = pd.read_csv(
        "forecast_probabilities.csv"
    )
    transition_matrix = pd.read_csv(
        "transition_matrix.csv"
    ).values

    forecast_df["Date"] = pd.to_datetime(
        forecast_df["Date"]
    )

    forecast_df = (
        forecast_df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # Merge datasets
    # ------------------------------------------------------------
    df = forecast_df.merge(
        prices_df[
            [
                "Date",
                "Close",
                "SMA20",
                "SMA50",
                "RSI14",
                "BB_Upper",
                "BB_Lower",
            ]
        ],
        on="Date",
        how="inner",
    )

    

    df["Target_Position"] = df.apply(
        compute_position_row,
        axis=1,
        transition_matrix=transition_matrix,
    )

    # ------------------------------------------------------------
    # Compute trade size
    # ------------------------------------------------------------
    df["Trade_Size"] = (
        df["Target_Position"]
        - df["Target_Position"].shift(1)
    )

    df["Trade_Size"] = (
        df["Trade_Size"]
        .fillna(df["Target_Position"])
    )

    # ------------------------------------------------------------
    # Save output
    # ------------------------------------------------------------
    output = df[
        [
            "Date",
            "Target_Position",
            "Trade_Size",
        ]
    ]

    output.to_csv(
        "signals_strategy_3.csv",
        index=False,
    )

    print("signals_strategy_3_5.csv saved.")

    print("\nAverage Target Position:")
    print(
        output["Target_Position"].describe()
    )

    print("\nAverage Trade Size:")
    print(
        output["Trade_Size"].describe()
    )