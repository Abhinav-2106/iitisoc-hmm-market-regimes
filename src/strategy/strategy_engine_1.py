STATE_NAMES = {
    0: "Normal Bull",
    1: "Correction",
    2: "Neutral/Recovery",
    3: "Crisis/Panic",
    4: "Aggressive Bull",
    5: "Calm Bull"
}

ALLOCATION_MAP = {
    0: 1.0,
    1: 0.0,
    2: 0.5,
    3: 0.0,
    4: 1.0,
    5: 1.0
}


def generate_signal(current_state):
    
    allocation = ALLOCATION_MAP[current_state]

    if allocation > 0.75:
        signal = "BUY"

    elif allocation > 0:
        signal = "HOLD"

    else:
        signal = "CASH"

    return signal, allocation