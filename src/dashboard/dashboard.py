import streamlit as st

from loader import load_dashboard_data
from metrics import add_rsi
from plots import (
    regime_price_chart,
    probability_chart,
    transition_heatmap,
    gk_volatility_chart,
    rsi_chart,
    risk_chart
)
st.set_page_config(
    page_title="Market Regime Dashboard",
    layout="wide"
)
st.title("Market Regime Classification using HMM")
st.write("NIFTY 50 Regime Analysis and Strategy Backtesting")
# Load data
data = load_dashboard_data()
market = add_rsi(data.market_data)
# Sidebar
st.sidebar.header("Filters")
start_date = st.sidebar.date_input(
    "Start Date",
    market["Date"].min().date()
)
end_date = st.sidebar.date_input(
    "End Date",
    market["Date"].max().date()
)
states = sorted(market["State"].dropna().unique())
selected_states = st.sidebar.multiselect(
    "States",
    states,
    default=states
)
# Apply filters
filtered = market[
    (market["Date"].dt.date >= start_date) &
    (market["Date"].dt.date <= end_date)
]
filtered = filtered[
    filtered["State"].isin(selected_states)
]
# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Market Regimes",
    "HMM Analysis",
    "Strategy Performance",
    "Risk Analytics",
    "Model Diagnostics"
])
with tab1:
    st.header("Market Regimes")
    st.plotly_chart(
        regime_price_chart(filtered),
        use_container_width=True
    )
    st.subheader("State Probabilities")
    st.plotly_chart(
        probability_chart(filtered),
        use_container_width=True
    )
with tab2:

    st.header("HMM Analysis")
    col1, col2 = st.columns(2)
    with col1:

        st.subheader("Transition Matrix")
        st.plotly_chart(
            transition_heatmap(data.transition_matrix),
            use_container_width=True
        )

    with col2:
        st.subheader("Regime Summary")

        st.dataframe(
            data.regime_summary,
            use_container_width=True,
            hide_index=True
        )
    st.subheader("State Characteristics")

    st.dataframe(
        data.state_characteristics,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("GK Volatility Distribution")
    if "gk_volatility" in filtered.columns:
        st.plotly_chart(
            gk_volatility_chart(filtered),
            use_container_width=True
        )
    else:
        st.warning("gk volatility column not found.")
    st.subheader("RSI Distribution")
    st.plotly_chart(
        rsi_chart(filtered),
        use_container_width=True
    )
with tab3:
    st.header("Strategy Performance")
    st.subheader("In-Sample Performance")
    st.dataframe(
        data.metrics_in_sample,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("Out-of-Sample Performance")

    st.dataframe(
        data.metrics_out_of_sample,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("Yearly Performance")
    st.dataframe(
        data.metrics_yearly,
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.header("Risk Analytics")
    sample = st.radio(
        "Select Dataset",
        ["In Sample", "Out of Sample"],
        horizontal=True
    )
    if sample == "In Sample":
        risk_data = data.metrics_in_sample
    else:
        risk_data = data.metrics_out_of_sample
    st.subheader("Performance Metrics")
    st.dataframe(
        risk_data,
        use_container_width=True,
        hide_index=True
    )
    metric_options = [
        col for col in [
            "CAGR",
            "Sharpe",
            "Sortino",
            "Max Drawdown",
            "Calmar",
            "Win Rate"
        ]
        if col in risk_data.columns
    ]
    if metric_options:
        selected_metric = st.selectbox(
            "Select Metric",
            metric_options
        )
        st.plotly_chart(
            risk_chart(risk_data, selected_metric),
            use_container_width=True
        )
with tab5:

    st.header("Model Diagnostics")
    st.subheader("State Persistence")
    st.dataframe(
        data.persistence_metrics,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("Backtesting Persistence")
    st.dataframe(
        data.persistence_bktest,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("Model Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Number of States",
            int(market["State"].nunique())
        )
    with col2:
        st.metric(
            "Observations",
            len(market)
        )
    with col3:
        st.metric(
            "Start Year",
            market["Date"].min().year
        )
