from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

df = pd.read_csv(ROOT / "data" / "features.csv")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# -----------------------------
# Log Returns
# -----------------------------
axes[0].hist(
    df["Log_Return"],
    bins=50,
)

axes[0].set_title("Log Returns")
axes[0].set_xlabel("Value")
axes[0].set_ylabel("Frequency")

# -----------------------------
# GK Volatility
# -----------------------------
axes[1].hist(
    df["gk_volatility"],
    bins=50,
)

axes[1].set_title("GK Volatility")
axes[1].set_xlabel("Value")

# -----------------------------
# Trading Range
# -----------------------------
axes[2].hist(
    df["Range"],
    bins=50,
)

axes[2].set_title("Trading Range")
axes[2].set_xlabel("Value")

plt.tight_layout()

plt.savefig(
    ROOT / "data" / "features_distribution.png",
    dpi=300,
    bbox_inches="tight",
)

plt.show()