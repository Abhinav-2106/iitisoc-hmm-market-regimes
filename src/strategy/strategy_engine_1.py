# Importing libs
import pandas as pd
from pathlib import Path

# updated num_states
NUM_STATES = 5

# Interpretation of the states
STATE_NAMES = {
    0: "Strong Bull",
    1: "Normal Bull",
    2: "Bear Market",
    3: "Extreme Event",
    4: "Correction",
}

# Static portfolio weights 
STATE_WEIGHTS = {
    0: 1.00,
    1: 0.85,
    2: 0.00,
    3: 0.00,
    4: 0.40,
}

# allocation = dot product of prob vector and weights
def compute_allocation(row):
    allocation = 0.0

    for state in range(NUM_STATES):
        allocation += (
            row[f"State_{state}"]
            * STATE_WEIGHTS[state]
        )

    return allocation

def main():

    # declaring path
    root = Path(__file__).resolve().parents[2]

    # downloading the raw probabilites
    df = pd.read_csv(
        root / "data" / "state_probabilities.csv"
    )

    # for every row call compute_allocation
    df["Target_Position"] = df.apply(
        compute_allocation,
        axis=1,
    )

    # trade size = difference in positions
    df["Trade_Size"] = (
        df["Target_Position"]
        - df["Target_Position"].shift(1)
    )

    # Initialize the first trade from an empty portfolio.
    df["Trade_Size"] = (
        df["Trade_Size"]
        .fillna(df["Target_Position"])
    )

    # extract the final strategy signals
    output = df[[
        "Date",
        "Target_Position",
        "Trade_Size",
    ]]

    # saving the results
    output.to_csv(
        root / "data" / "signals_strategy_1.csv",
        index=False,
    )

if __name__ == "__main__":
    main()