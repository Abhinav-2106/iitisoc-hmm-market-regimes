from pathlib import Path

import streamlit as st
from plots import (
    regime_price_chart,
    probability_chart,
)

from loader import load_dashboard_data


# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="Market Regime Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

dashboard = load_dashboard_data()


# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("Dashboard Controls")

min_date = dashboard.market_data["Date"].min()
max_date = dashboard.market_data["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_state = st.sidebar.selectbox(
    "Highlight Regime",
    ["All"] + sorted(
        dashboard.market_data["State"].unique().tolist()
    )
)

st.sidebar.divider()

st.sidebar.markdown("### Dataset")

st.sidebar.write(
    f"Observations : {len(dashboard.market_data):,}"
)

st.sidebar.write(
    f"States : {dashboard.market_data['State'].nunique()}"
)

st.sidebar.write(
    f"Features : 5"
)


# -------------------------------------------------------
# Header
# -------------------------------------------------------

st.title("Hidden Markov Market Regime Dashboard")

st.caption(
    "IITI • SoC Project"
)

st.divider()




#KPI

latest = dashboard.market_data.iloc[-1]

current_state = int(latest["State"])

current_state = int(latest["State"])

probability_column = f"State_{current_state}"

current_probability = latest[probability_column]

expected_duration = dashboard.persistence_metrics.loc[
    dashboard.persistence_metrics["State"] == current_state,
    "Expected_Duration"
].iloc[0]

persistence = dashboard.persistence_metrics.loc[
    dashboard.persistence_metrics["State"] == current_state,
    "Persistence"
].iloc[0]


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current State",
    current_state
)

col2.metric(
    "Confidence",
    f"{current_probability*100:.2f}%"
)

col3.metric(
    "Persistence",
    f"{persistence:.3f}"
)

col4.metric(
    "Expected Duration",
    f"{expected_duration:.1f} Days"
)

st.divider()





market_tab, hmm_tab, strategy_tab, risk_tab, diagnostics_tab = st.tabs(
    [
        "Market Regimes",
        "HMM Analysis",
        "Strategy Performance",
        "Risk Analytics",
        "Diagnostics"
    ]
)


with market_tab:

    st.header("Market Regimes")

    st.subheader("Price Coloured by Regime")

    st.plotly_chart(
        regime_price_chart(dashboard.market_data),
        use_container_width=True,
    )

    st.divider()

    st.subheader("State Probabilities")

    st.plotly_chart(
        probability_chart(dashboard.market_data),
        use_container_width=True,
    )
