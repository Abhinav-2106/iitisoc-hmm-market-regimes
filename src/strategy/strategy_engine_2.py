import pandas as pd
import os

STATE_WEIGHTS = {
    0: 1.0,   # Normal Bull
    1: 0.25,  # Correction
    2: 0.50,  # Neutral/Recovery
    3: 0.0,   # Crisis/Panic
    4: 1.0,   # Aggressive Bull
    5: 0.75   # Calm Bull
}


def compute_allocation(row):

    allocation = 0

    for state, weight in STATE_WEIGHTS.items():

        allocation += (
            row[f"Forecast_State_{state}"]
            * weight
        )

    return allocation


if __name__ == "__main__":

    path = os.path.realpath("strategy_engine_2.py")
    data_dir = os.path.dirname(
        os.path.dirname(path)
    ).replace("src", "data")

    os.chdir(data_dir)

    df = pd.read_csv(
        "forecast_probabilities.csv"
    )

    df["Target_Position"] = df.apply(
        compute_allocation,
        axis=1
    )

    df["Trade_Size"] = (
        df["Target_Position"]
        - df["Target_Position"].shift(1)
    )

    df["Trade_Size"] = (
        df["Trade_Size"]
        .fillna(df["Target_Position"])
    )

    df.to_csv(
        "signals_strategy_2.csv",
        index=False
    )

    print(df[[
        "Date",
        "Target_Position",
        "Trade_Size"
        ]].head()
    )