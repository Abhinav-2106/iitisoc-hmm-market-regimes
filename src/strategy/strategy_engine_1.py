import pandas as pd

num_states = 6

STATE_NAMES = {
    0: "Normal Bull",        # BUll state
    1: "Correction",         # BEAR state
    2: "Neutral/Recovery",   # SIDEWAYS state
    3: "Crisis/Panic",       # BEAR state
    4: "Aggressive Bull",    # BULL states
    5: "Calm Bull"           # BULL state
}

STATE_WEIGHTS = {            # subject to change
    0: 1.0,
    1: 0.25,
    2: 0.50,
    3: 0.0,
    4: 1.0,
    5: 0.75
}


def compute_allocation(row):
    allocation = 0

    for state in range(num_states):
        
        allocation += (
            row[f"State_{state}"]
            * STATE_WEIGHTS[state]
        )

    return allocation


    
df = pd.read_csv(
    "data/state_probabilities.csv"
)

df["Target_Position"] = df.apply(
    compute_allocation,
    axis=1
)

df["Trade_Size"] = df["Target_Position"] - df["Target_Position"].shift(1)

# fill first value
df["Trade_Size"] = df["Trade_Size"].fillna(df["Target_Position"])

df.to_csv(
    "data/signals_strategy_1.csv",
    index=False
)