from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

NUM_STATES = 5

STATE_NAMES = {
    0: "Strong Bull",
    1: "Normal Bull",
    2: "Bear Market",
    3: "Extreme Event",
    4: "Correction",
}

STATE_WEIGHTS = {
    0: 1.00,
    1: 0.75,
    2: 0.00,
    3: 0.00,
    4: 0.40,
}


def compute_allocation(row):

    allocation = 0.0

    for state in range(NUM_STATES):

        allocation += (
            row[f"Forecast_State_{state}"]
            * STATE_WEIGHTS[state]
        )

    return allocation


if __name__ == "__main__":

    df = pd.read_csv(
        ROOT / "data" / "forecast_probabilities.csv"
    )

    df["Target_Position"] = df.apply(
        compute_allocation,
        axis=1,
    )

    df["Trade_Size"] = (
        df["Target_Position"]
        - df["Target_Position"].shift(1)
    )

    df["Trade_Size"] = (
        df["Trade_Size"]
        .fillna(df["Target_Position"])
    )

    output = df[
        [
            "Date",
            "Target_Position",
            "Trade_Size",
        ]
    ]

    output.to_csv(
        ROOT / "data" / "signals_strategy_2.csv",
        index=False,
    )