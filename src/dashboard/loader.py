from pathlib import Path

import streamlit as st
import pandas as pd


# ------------------------------------------------------------------
# Project Paths
# ------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"


# ------------------------------------------------------------------
# Dashboard Data Container
# ------------------------------------------------------------------

class DashboardData:
    """
    Stores every dataset required by the dashboard.
    """

    def __init__(self):

        # Raw datasets
        self.clean_data = None
        self.features = None
        self.states = None
        self.state_probabilities = None
        self.transition_matrix = None
        self.state_characteristics = None
        self.persistence_metrics = None
        self.regime_summary = None

        # Combined dataset
        self.market_data = None

        # Models
        self.hmm_model = None
        self.scaler = None


# ------------------------------------------------------------------
# Loader
# ------------------------------------------------------------------

@st.cache_resource
def load_dashboard_data():

    dashboard = DashboardData()

    # ---------------------------
    # CSV Files
    # ---------------------------

    dashboard.clean_data = pd.read_csv(
        DATA_DIR / "clean_data.csv",
        parse_dates=["Date"]
    )

    dashboard.features = pd.read_csv(
        DATA_DIR / "features.csv",
        parse_dates=["Date"]
    )

    dashboard.states = pd.read_csv(
        DATA_DIR / "states.csv",
        parse_dates=["Date"]
    )

    dashboard.state_probabilities = pd.read_csv(
        DATA_DIR / "state_probabilities.csv",
        parse_dates=["Date"]
    )

    dashboard.transition_matrix = pd.read_csv(
        DATA_DIR / "transition_matrix.csv"
    )

    dashboard.state_characteristics = pd.read_csv(
        DATA_DIR / "state_characteristics.csv"
    )

    dashboard.persistence_metrics = pd.read_csv(
        DATA_DIR / "persistence_metrics.csv"
    )

    dashboard.regime_summary = pd.read_csv(
        DATA_DIR / "regime_summary.csv"
    )

    # ---------------------------
    # Merge datasets
    # ---------------------------

    dashboard.market_data = (

        dashboard.clean_data

        .merge(
            dashboard.features,
            on="Date",
            how="left"
        )

        .merge(
            dashboard.states,
            on="Date",
            how="left"
        )

        .merge(
            dashboard.state_probabilities,
            on="Date",
            how="left"
        )

    )

    return dashboard

