# importing libraries
import pandas as pd
import numpy as np
from pathlib import Path

# importing local files
from strategies import momentum, mean_reversion, risk

# declaring the number of states
NUM_STATES = 5

# Interpretation fo states
BULL_STATES    = [0, 1]   # Both positive Sharpe → Momentum
NEUTRAL_STATES = [4]      # Correction, persistent → Mean Reversion
BEAR_STATES    = [2, 3]   # Negative return, crisis → Cash


def aggregate_regimes(row: pd.Series):
    """
    Aggregate the five forecasted HMM states into
    Bull, Neutral and Bear probabilities.
    """

    bull_prob = (
        row["Forecast_State_0"]
        + row["Forecast_State_1"]
    )

    neutral_prob = (
        row["Forecast_State_4"]
    )

    bear_prob = (
        row["Forecast_State_2"]
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
    bull_signal = bull_prob * (0.6 + 0.4 * momentum_score)
    neutral_signal = neutral_prob * mr_score

    # Forecast probability vector
    forecast_probs = np.array([
        row[f"Forecast_State_{i}"]
        for i in range(5)
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

def sanity_checks(df):

    df["Momentum_Score"] = df.apply(
        lambda r: momentum.score(r["Close"], r["SMA20"], r["SMA50"]),
        axis=1
    )
    df["MR_Score"] = df.apply(
        lambda r: mean_reversion.score(
            r["Close"], r["RSI14"], r["BB_Upper"], r["BB_Lower"]
        ),
        axis=1
    )
    df["Bull_Prob"] = df.apply(
        lambda r: r["Forecast_State_0"] + r["Forecast_State_1"], axis=1
    )

    print(f"Momentum_Score mean : {df['Momentum_Score'].mean():.4f}")
    print(f"MR_Score mean       : {df['MR_Score'].mean():.4f}")

    print(f"\nBull_Prob mean      : {df['Bull_Prob'].mean():.4f}")
    print(f"\nTarget_Position mean: {df['Target_Position'].mean():.4f}")
    print(f"\nTurnover (mean daily change):")

    changes = df["Target_Position"].diff().abs().dropna()
    print(f"  Mean change         : {changes.mean():.4f}")
    print(f"  Days > 0.10 change  : {(changes > 0.10).mean():.1%}")

def main():
    # declaring path
    root = Path(__file__).resolve().parents[2]

    # Load price data
    prices_df = pd.read_csv(
        root / "data" / "clean_data.csv"
    )

    prices_df["Date"] = pd.to_datetime(
        prices_df["Date"]
    )

    prices_df = (
        prices_df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # Compute strategy indicators
    prices_df = momentum.compute_indicators(prices_df)

    prices_df = mean_reversion.compute_indicators(prices_df)

    # Load forecast probabilities
    forecast_df = pd.read_csv(
        root / "data"/ "forecast_probabilities.csv"
    )
    # load transition matrix
    transition_matrix = pd.read_csv(
        root / "data" / "transition_matrix.csv"
    ).values

    forecast_df["Date"] = pd.to_datetime(
        forecast_df["Date"]
    )

    forecast_df = (
        forecast_df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # Merge datasets
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

    # Compute trade size
    df["Trade_Size"] = (
        df["Target_Position"]
        - df["Target_Position"].shift(1)
    )

    df["Trade_Size"] = (
        df["Trade_Size"]
        .fillna(df["Target_Position"])
    )
    
    # sanity_checks(df)
    
    # Save output
    output = df[
        [
            "Date",
            "Target_Position",
            "Trade_Size",
        ]
    ]

    output.to_csv(
        root / "data" / "signals_strategy_3.csv",
        index=False,
    )

if __name__ == "__main__":
    main()