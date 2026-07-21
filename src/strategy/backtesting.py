import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

root = Path(__file__).resolve().parents[2]
clean_data = root / "data"

TRADING_DAYS = 252
commission = 0.0005  # Broker commission
slippagefactor = 0.02 # Slippage factor for daily volatility
POSITION_THRESHOLD = 0.05 # Ignore trades if position change is less than 10%

def load_data():
    prices = pd.read_csv(clean_data / "clean_data.csv") # Loading the clean_data.csv
    prices["Date"] = pd.to_datetime(prices["Date"])

    # Load all 3 precomputed signal files
    try:
        sig1 = pd.read_csv(clean_data / "signals_strategy_1.csv")
        sig2 = pd.read_csv(clean_data / "signals_strategy_2.csv")
        sig3 = pd.read_csv(clean_data / "signals_strategy_3.csv")

        sig1["Date"] = pd.to_datetime(sig1["Date"])
        sig2["Date"] = pd.to_datetime(sig2["Date"])
        sig3["Date"] = pd.to_datetime(sig3["Date"])
    except FileNotFoundError as e:
        print(f"Couldn't load csv file from {e}")
        return None, None, None, None

    return prices, sig1, sig2, sig3

def run_backtest(prices, signals, threshold=POSITION_THRESHOLD):
    # Fusing prices of nifty50 with signals
    bt = prices.merge(signals, on="Date", how="inner")

    # Ensure columns match expected naming conventions
    if "Target_Position" not in bt.columns:
        # Fallback in case the output column is named "signal" or "position"
        signal_col = [col for col in bt.columns if col.lower() in ["signal", "position"]][0]
        bt["Target_Position"] = bt[signal_col]

    bt["Return"] = bt["Close"].pct_change() # Changes in nifty50 prices day by day

    # Extract the shifted targets to prevent look ahead bias
    shifted_targets = bt["Target_Position"].shift(1).fillna(0).values

    # Threshold Filter Logic
    actual_positions = np.zeros(len(shifted_targets))
    current_pos = 0.0

    # Loop to check position difference
    for i in range(len(shifted_targets)):
        # Only trade if the difference is greater than or equal to the threshold
        if abs(shifted_targets[i] - current_pos) >= threshold:
            current_pos = shifted_targets[i]

        actual_positions[i] = current_pos

    bt["Position"] = actual_positions

    # Transaction cost
    bt["Position_Change"] = bt["Position"].diff().abs().fillna(bt["Position"].abs()) # Calculating turnover
    dslippage = bt["Return"].abs() * slippagefactor # Dynamic slippage
    bt["Cost"] = bt["Position_Change"] * (commission + dslippage) # Total cost

    bt["Strategy_Return"] = (bt["Position"] * bt["Return"]) - bt["Cost"]
    bt["Strategy_Return"] = bt["Strategy_Return"].fillna(0)

    bt["Equity"] = (1 + bt["Strategy_Return"]).cumprod()
    bt["Market_Equity"] = (1 + bt["Return"].fillna(0)).cumprod()

    return bt

def calculate_metrics(bt, label="Strategy"):
    # CAGR
    years = (bt["Date"].iloc[-1] - bt["Date"].iloc[0]).days / 365.25
    cagr = (bt["Equity"].iloc[-1] ** (1 / years)) - 1 if years > 0 else 0

    # Sharpe
    std = bt["Strategy_Return"].std()
    sharpe = (bt["Strategy_Return"].mean() / std) * np.sqrt(TRADING_DAYS) if std > 0 else 0

    # Sortino
    downside = bt["Strategy_Return"][bt["Strategy_Return"] < 0]
    sortino = (bt["Strategy_Return"].mean() / downside.std()) * np.sqrt(TRADING_DAYS) if not downside.empty else 0

    # Maximum drawdown
    drawdown = (bt["Equity"] / bt["Equity"].cummax()) - 1
    max_dd = drawdown.min()

    # Calmar
    calmar = cagr / abs(max_dd) if max_dd < 0 else 0

    # Win rate
    win_rate = (bt[bt["Position"] != 0]["Strategy_Return"] > 0).mean()

    return {
        "Strategy": label,
        "CAGR": f"{cagr:.2%}",
        "Sharpe": round(sharpe, 2),
        "Sortino": round(sortino, 2),
        "Max Drawdown": f"{max_dd:.2%}",
        "Calmar": round(calmar, 2),
        "Win Rate": f"{win_rate:.2%}"
    }

def compare_equity(bt_dict):
    plt.figure(figsize=(12, 6))
    for name, bt in bt_dict.items():
        plt.plot(bt["Date"], bt["Equity"], label=name)
    plt.title(f"Strategies vs Benchmark (Threshold: {POSITION_THRESHOLD})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('plot.png', dpi=300)
    plt.show()


def main():
    print("Loading signals and data")
    prices, sig1, sig2, sig3 = load_data()

    if prices is None:
        return

    print(f"Running Backtest with a {POSITION_THRESHOLD*100}% trade threshold")

    # Strategy 1
    bt1 = run_backtest(prices, sig1)

    # Strategy 2
    bt2 = run_backtest(prices, sig2)

    # Strategy 3
    bt3 = run_backtest(prices, sig3)

    # Buy & Hold
    buy_hold_signals = pd.DataFrame({"Date": prices["Date"], "Target_Position": 1.0})
    bt_bh = run_backtest(prices, buy_hold_signals, threshold=0.0) # BH has no threshold

    results_bt = {
        "Strategy 1": bt1,
        "Strategy 2": bt2,
        "Strategy 3": bt3,
        "Buy & Hold": bt_bh
    }

    metrics_list = [
        calculate_metrics(bt1, label="Strategy 1"),
        calculate_metrics(bt2, label="Strategy 2"),
        calculate_metrics(bt3, label="Strategy 3"),
        calculate_metrics(bt_bh, label="Buy & Hold")
    ]

    print("\nPERFORMANCE METRICS")
    metrics_df = pd.DataFrame(metrics_list)
    print(metrics_df.to_string(index=False))

    print("\nPlotting Equity Curves")
    compare_equity(results_bt)

if __name__ == "__main__":
    main()