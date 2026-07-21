# importing libs
from pathlib import Path
import numpy as np
import pandas as pd

# declaring path
root = Path(__file__).resolve().parents[2]

# number of states
NUM_STATES = 5

def forecast_probs(row, transition_matrix):

    current_probs = np.array([
        row[f"State_{i}"]
        for i in range(NUM_STATES)
    ])

    forecast_probs = (
        current_probs
        @ transition_matrix
    )

    return pd.Series(
        forecast_probs,
        index=[
            f"Forecast_State_{i}"
            for i in range(NUM_STATES)
        ]
    )


def load_matrix():

    transition_matrix = pd.read_csv(
        root / "data" / "transition_matrix.csv"
    )

    return transition_matrix.values

def main():

    probs_df = pd.read_csv(
        root / "data" / "state_probabilities.csv"
    )

    transition_matrix = load_matrix()

    forecasts = probs_df.apply(
        forecast_probs,
        axis=1,
        transition_matrix=transition_matrix,
    )

    result = pd.concat(
        [probs_df, forecasts],
        axis=1,
    )

    result.to_csv(
        root / "data" / "forecast_probabilities.csv",
        index=False,
    )

if __name__ == "__main__":
    main()