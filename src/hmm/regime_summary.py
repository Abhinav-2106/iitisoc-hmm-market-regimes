from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def main():

    state_df = pd.read_csv(
        DATA / "state_characteristics.csv"
    )

    persistence_df = pd.read_csv(
        DATA / "persistence_metrics.csv"
    )

    features = pd.read_csv(
        DATA / "features.csv"
    )

    states = pd.read_csv(
        DATA / "states.csv"
    )

    features = features.merge(
        states,
        on="Date",
        how="left"
    )

    extra_stats = []

    for state in sorted(features["State"].unique()):

        state_data = features[
            features["State"] == state
        ]

        extra_stats.append({

            "State": state,

            "Return_Std":
            state_data["Log_Return"].std(),

            "Mean_GK_Volatility":
            state_data["GK_Volatility"].mean()

        })

    extra_stats = pd.DataFrame(
        extra_stats
    )

    summary = (
        state_df
        .merge(
            persistence_df,
            on="State",
            how="left"
        )
        .merge(
            extra_stats,
            on="State",
            how="left"
        )
    )

    summary.insert(
        1,
        "Regime_Name",
        [
            f"State {i}"
            for i in summary["State"]
        ]
    )

    columns = [

        "State",

        "Regime_Name",

        "Frequency",

        "Percentage",

        "Mean_Return",

        "Return_Std",

        "Mean_GK_Volatility",

        "Sharpe_Ratio",

        "Sortino_Ratio",

        "Expected_Duration",

        "Persistence",

    ]

    summary = summary[
        [
            column
            for column in columns
            if column in summary.columns
        ]
    ]

    summary.to_csv(
        DATA / "regime_summary.csv",
        index=False
    )

    print(summary)

    print(
        "\nSaved regime_summary.csv"
    )


if __name__ == "__main__":
    main()
