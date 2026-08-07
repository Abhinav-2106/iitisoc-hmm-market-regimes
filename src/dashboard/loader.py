from pathlib import Path
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


class DashboardData:

    def __init__(self):

        # HMM files
        self.clean_data = None
        self.features = None
        self.states = None
        self.state_probabilities = None
        self.transition_matrix = None
        self.state_characteristics = None
        self.persistence_metrics = None
        self.regime_summary = None

        # Backtesting files
        self.metrics_in_sample = None
        self.metrics_out_of__sample = None
        self.metrics_yearly = None
        self.persistence_bktest = None

        # Final merged dataframe
        self.market_data = None


@st.cache_data
def load_dashboard_data():

    data = DashboardData()

    try:

        data.clean_data = pd.read_csv(
            DATA_DIR / "clean_data.csv",
            parse_dates=["Date"]
        )

        data.features = pd.read_csv(
            DATA_DIR / "features.csv",
            parse_dates=["Date"]
        )

        data.states = pd.read_csv(
            DATA_DIR / "states.csv",
            parse_dates=["Date"]
        )

        data.state_probabilities = pd.read_csv(
            DATA_DIR / "state_probabilities.csv",
            parse_dates=["Date"]
        )

        data.transition_matrix = pd.read_csv(
            DATA_DIR / "transition_matrix.csv"
        )

        data.state_characteristics = pd.read_csv(
            DATA_DIR / "state_characteristics.csv"
        )

        data.persistence_metrics = pd.read_csv(
            DATA_DIR / "persistence_metrics.csv"
        )

        data.regime_summary = pd.read_csv(
            DATA_DIR / "regime_summary.csv"
        )

        # Backtesting files

        data.metrics_in_sample = pd.read_csv(
            DATA_DIR / "metrics_in_sample.csv"
        )

        data.metrics_out_of_sample = pd.read_csv(
            DATA_DIR / "metrics_out_of_sample.csv"
        )

        data.metrics_yearly = pd.read_csv(
            DATA_DIR / "metrics_yearly_detailed.csv"
        )

        data.persistence_bktest = pd.read_csv(
            DATA_DIR / "persistence_metrics_bktest.csv"
        )

    except FileNotFoundError as e:

        st.error(f"Missing file: {e}")
        st.stop()

    # Merge data

    data.market_data = (
        data.clean_data
        .merge(data.features, on="Date", how="left")
        .merge(data.states, on="Date", how="left")
        .merge(data.state_probabilities, on="Date", how="left")
    )

    return data
