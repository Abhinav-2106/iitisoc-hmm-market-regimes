import numpy as np

def forecast(P, curr_regime_prob):
    return np.matmul(curr_regime_prob , P)