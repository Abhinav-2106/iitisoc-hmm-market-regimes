import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Data Loading

def load_data():
    ROOT = Path(__file__).resolve().parents[2]

    prices = pd.read_csv(
        ROOT / "data" / "clean_data.csv"
    )

    signals = pd.read_csv(
        ROOT / "data" / "signals_strategy_2.csv"
    )

    return prices, signals


# Backtest Engine

def run_backtest(prices, signals):

    df = prices.merge(
        signals,
        on="Date",
        how="inner"
    )

    df["Date"] = pd.to_datetime(df["Date"])

    df["Return"] = (
        df["Close"]
        .pct_change()
    )

    df["Strategy_Return"] = (
        df["Target_Position"]
        .shift(1)
        * df["Return"]
    )

    df["Strategy_Return"] = (
        df["Strategy_Return"]
        .fillna(0)
    )


    df["Equity"] = (
        1 + df["Strategy_Return"]
    ).cumprod()

    # Buy & Hold Equity Curve
    df["Market_Equity"] = (
        1 + df["Return"].fillna(0)
    ).cumprod()

    return df


# Performance Metrics

def calculate_cagr(df):

    years = (
        (df["Date"].iloc[-1] - df["Date"].iloc[0]).days
        / 365.25
    )

    final_equity = df["Equity"].iloc[-1]

    cagr = (
        final_equity ** (1 / years)
        - 1
    )

    return cagr


def calculate_sharpe(df):

    sharpe = (
        df["Strategy_Return"].mean()
        /
        df["Strategy_Return"].std()
    ) * (252 ** 0.5)

    return sharpe


def calculate_max_drawdown(df):

    df["Rolling_Max"] = (
        df["Equity"]
        .cummax()
    )

    df["Drawdown"] = (
        df["Equity"]
        /
        df["Rolling_Max"]
        - 1
    )

    return df["Drawdown"].min()


# Visualization

def plot_equity_curve(df):

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["Date"],
        df["Equity"]
    )

    plt.title("Strategy Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")

    plt.grid(True)
    plt.show()


def compare_with_buy_hold(df):

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["Date"],
        df["Equity"],
        label="Strategy"
    )

    plt.plot(
        df["Date"],
        df["Market_Equity"],
        label="Buy & Hold"
    )

    plt.title("Strategy vs Buy & Hold")

    plt.legend()
    plt.grid(True)

    plt.show()


# Main

def main():

    prices, signals = load_data()

    df = run_backtest(
        prices,
        signals
    )

    cagr = calculate_cagr(df)
    sharpe = calculate_sharpe(df)
    max_dd = calculate_max_drawdown(df)

    print("=" * 40)
    print("BACKTEST RESULTS")
    print("=" * 40)

    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.2%}")

    plot_equity_curve(df)

    compare_with_buy_hold(df)


if __name__ == "__main__":
    main()