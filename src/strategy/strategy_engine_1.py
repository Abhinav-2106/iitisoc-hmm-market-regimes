import pandas as pd

STATE_NAMES = {
    0: "Normal Bull",
    1: "Correction",
    2: "Neutral/Recovery",
    3: "Crisis/Panic",
    4: "Aggressive Bull",
    5: "Calm Bull"
}

STATE_WEIGHTS = { # subject to change
    0: 1.0,
    1: 0.25,
    2: 0.50,
    3: 0.0,
    4: 1.0,
    5: 0.75
}


def compute_allocation(row):
    allocation = 0

    for state in range(6):

        allocation += (
            row[f"State_{state}"]
            * STATE_WEIGHTS[state]
        )

    return allocation

def allocation_to_signal(allocation):

    if allocation >= 0.75:
        return "BUY"

    elif allocation >= 0.25:
        return "HOLD"
    else:
        return "CASH"
    
df = pd.read_csv(
    "state_probabilities.csv"
)

df["Allocation"] = df.apply(
    compute_allocation,
    axis=1
)

df["Signal"] = df["Allocation"].apply(
    allocation_to_signal
)