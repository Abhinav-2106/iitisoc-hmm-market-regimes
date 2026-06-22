import numpy as np
import pandas as pd
import os

def forecast_probs(row, transitional_matrix):

    current_probs = np.array([
        row["State_0"],
        row["State_1"],
        row["State_2"],
        row["State_3"],
        row["State_4"],
        row["State_5"]
    ])

    forecast_probs =  current_probs @ transitional_matrix

    return pd.Series(
        forecast_probs,
        index=[f"Forecast_State_{i}" for i in range(6)]
    )

def load_matrix():

    trans_matrix = pd.read_csv(
        "transition_matrix.csv"
    )

    return trans_matrix.values


if __name__ == "__main__":

    path = os.path.realpath("transitional_forecast.py")
    dir = os.path.dirname(os.path.dirname(path)).replace("src", "data")

    os.chdir(dir)

    probs_df = pd.read_csv(
        "state_probabilities.csv"
    )

    transition_matrix = load_matrix()

    forecasts = probs_df.apply(
        forecast_probs,
        axis=1,
        transitional_matrix=transition_matrix
    )

    result = pd.concat(
        [probs_df, forecasts],
        axis=1
    )

    result.to_csv(
        "forecast_probabilities.csv",
        index=False
    )

    print(result.head())