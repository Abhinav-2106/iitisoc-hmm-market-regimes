import numpy as np


def expected_stability(
    forecast_probs: np.ndarray,
    transition_matrix: np.ndarray,
) -> float:
    """
    Expected regime stability.

    Computes

        Σ P(state_i) * T[i,i]
    """

    return float(
        np.dot(
            forecast_probs,
            np.diag(transition_matrix)
        )
    )


def apply_risk(
    bull_signal: float,
    neutral_signal: float,
    stability: float,
) -> float:
    """
    Bull signal is left untouched.

    Neutral signal is dampened using
    transition stability.
    """

    adjusted_neutral = (
        neutral_signal
        * stability
    )

    position = (
        bull_signal
        + adjusted_neutral
    )

    return float(
        np.clip(
            position,
            0.0,
            1.0
        )
    )