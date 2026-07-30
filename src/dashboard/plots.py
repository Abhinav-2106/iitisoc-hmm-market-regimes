import plotly.express as px
import plotly.graph_objects as go


STATE_COLORS = {
    0: "#ef4444",   # red
    1: "#22c55e",   # green
    2: "#3b82f6",   # blue
    3: "#f59e0b",   # orange
    4: "#8b5cf6",   # purple
}


#price vs regime

import plotly.graph_objects as go

STATE_COLORS = {
    0: "#EF4444",
    1: "#22C55E",
    2: "#3B82F6",
    3: "#F59E0B",
    4: "#8B5CF6",
}


def regime_price_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            line=dict(color="white", width=1),
            name="NIFTY"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="markers",
            marker=dict(
                size=6,
                color=df["State"],
                colorscale=[
                    [0.00, "#EF4444"],
                    [0.25, "#22C55E"],
                    [0.50, "#3B82F6"],
                    [0.75, "#F59E0B"],
                    [1.00, "#8B5CF6"]
                ],
                showscale=False
            ),
            name="Regime"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        hovermode="x unified",
        title="NIFTY Close with HMM Regimes",
        xaxis_title="Date",
        yaxis_title="Close Price"
    )

    return fig

def probability_chart(df):

    fig = go.Figure()

    colors = {
        "State_0": "#EF4444",
        "State_1": "#22C55E",
        "State_2": "#3B82F6",
        "State_3": "#F59E0B",
        "State_4": "#8B5CF6",
    }

    for column in [
        "State_0",
        "State_1",
        "State_2",
        "State_3",
        "State_4",
    ]:

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[column],
                mode="lines",
                name=column,
                line=dict(
                    width=2,
                    color=colors[column]
                )
            )
        )

    fig.update_layout(
        template="plotly_dark",
        height=550,
        title="Hidden State Probabilities",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Probability",
        legend_title="State"
    )

    fig.update_yaxes(
        range=[0, 1]
    )

    return fig

