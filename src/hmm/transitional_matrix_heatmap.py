import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def main():

    ROOT = Path(__file__).resolve().parents[2]

    data_dir = ROOT / "data"

    transition_matrix = pd.read_csv(
        data_dir / "transition_matrix.csv"
    )

    regime_summary = pd.read_csv(
        data_dir / "regime_summary.csv"
    )

    state_names = regime_summary["Regime_Name"]

    plt.figure(figsize=(8, 6))

    sns.heatmap(
        transition_matrix,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        linewidths=0.5,
        square=True,
        xticklabels=state_names,
        yticklabels=state_names,
        cbar_kws={
            "label": "Transition Probability"
        }
    )

    plt.title(
        "HMM Transition Matrix",
        fontsize=14,
        pad=12,
    )

    plt.xlabel("Next State")
    plt.ylabel("Current State")

    plt.tight_layout()

    plt.savefig(
        data_dir / "transition_matrix_heatmap.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


if __name__ == "__main__":
    main()