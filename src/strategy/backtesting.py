import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

root = Path(__file__).resolve().parents[2]
clean_data = root / "data"

TRADING_DAYS = 252
commission = 0.0005  # Broker commission
slippagefactor = 0.02 # Slippage factor for daily volatility
POSITION_THRESHOLD = 0.05 # Ignore trades if position change is less than 5%
OOS_START_DATE = "2020-01-01" # The date where Out-Of-Sample testing begins

# Data Loading
def load_data():
    prices = pd.read_csv(clean_data / "clean_data.csv")
    prices["Date"] = pd.to_datetime(prices["Date"])

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

# Backtest Engine
def run_backtest(prices, signals, threshold=POSITION_THRESHOLD, comm=commission, slip=slippagefactor):
    bt = prices.merge(signals, on="Date", how="inner")

    if "Target_Position" not in bt.columns:
        signal_col = [col for col in bt.columns if col.lower() in ["signal", "position"]][0]
        bt["Target_Position"] = bt[signal_col]

    bt["Return"] = bt["Close"].pct_change()
    shifted_targets = bt["Target_Position"].shift(1).fillna(0).values

    # Threshold Filter Logic
    actual_positions = np.zeros(len(shifted_targets))
    current_pos = 0.0

    for i in range(len(shifted_targets)):
        if abs(shifted_targets[i] - current_pos) >= threshold:
            current_pos = shifted_targets[i]
        actual_positions[i] = current_pos

    bt["Position"] = actual_positions

    # Transaction cost
    bt["Position_Change"] = bt["Position"].diff().abs().fillna(bt["Position"].abs())
    dslippage = bt["Return"].abs() * slip
    bt["Cost"] = bt["Position_Change"] * (comm + dslippage)

    bt["Strategy_Return"] = (bt["Position"] * bt["Return"]) - bt["Cost"]
    bt["Strategy_Return"] = bt["Strategy_Return"].fillna(0)

    bt["Equity"] = (1 + bt["Strategy_Return"]).cumprod()
    bt["Market_Equity"] = (1 + bt["Return"].fillna(0)).cumprod()

    return bt

# Metrics & Aggregation
def calculate_metrics(bt, label="Strategy"):
    if bt.empty: return {}

    years = (bt["Date"].iloc[-1] - bt["Date"].iloc[0]).days / 365.25
    cagr = ((bt["Equity"].iloc[-1] / bt["Equity"].iloc[0]) ** (1 / years)) - 1 if years > 0 else 0

    std = bt["Strategy_Return"].std()
    sharpe = (bt["Strategy_Return"].mean() / std) * np.sqrt(TRADING_DAYS) if std > 0 else 0

    downside = bt["Strategy_Return"][bt["Strategy_Return"] < 0]
    sortino = (bt["Strategy_Return"].mean() / downside.std()) * np.sqrt(TRADING_DAYS) if not downside.empty else 0

    drawdown = (bt["Equity"] / bt["Equity"].cummax()) - 1
    max_dd = drawdown.min()

    calmar = cagr / abs(max_dd) if max_dd < 0 else 0
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

def display_detailed_yearly_metrics(bt_dict):
    bh_bt = bt_dict["Buy & Hold"]

    # add a star if the strategy beats B&H
    def add_star(s_val, bh_val):
        try:
            # Strip '%' and convert to floats for mathematical comparison
            sv = float(str(s_val).replace('%', ''))
            bv = float(str(bh_val).replace('%', ''))

            # For CAGR, Sharpe, and Sortino Higher is better.
            # For Max Drawdown (negative values like -10% vs -30%): Higher (-10) is STILL better!
            if sv > bv:
                return f"{s_val} *"
            return str(s_val)
        except:
            return str(s_val)

    for name, bt in bt_dict.items():
        if name == "Buy & Hold":
            continue

        print("\n" + "="*95)
        print(f"YEARLY METRICS: {name} vs Buy & Hold")
        print("="*95)

        years = sorted(bt['Date'].dt.year.unique())
        yearly_stats = []

        for yr in years:
            # Isolate the specific year for both Strategy and Benchmark
            bt_yr = bt[bt['Date'].dt.year == yr].copy()
            bh_yr = bh_bt[bh_bt['Date'].dt.year == yr].copy()

            # Skip if there's insufficient data for the year
            if len(bt_yr) < 2:
                continue

            # Calculate full metrics suite for this specific year
            m_s = calculate_metrics(bt_yr, label=name)
            m_bh = calculate_metrics(bh_yr, label="Buy & Hold")

            # Build the comparison row
            row = {
                "Year": yr,
                "CAGR (Strat)": add_star(m_s.get("CAGR", "0%"), m_bh.get("CAGR", "0%")),
                "CAGR (B&H)": m_bh.get("CAGR", "0%"),
                "Sharpe (S)": add_star(m_s.get("Sharpe", 0), m_bh.get("Sharpe", 0)),
                "Sharpe (B&H)": m_bh.get("Sharpe", 0),
                "Sortino (S)": add_star(m_s.get("Sortino", 0), m_bh.get("Sortino", 0)),
                "Sortino (B&H)": m_bh.get("Sortino", 0),
                "MaxDD (S)": add_star(m_s.get("Max Drawdown", "0%"), m_bh.get("Max Drawdown", "0%")),
                "MaxDD (B&H)": m_bh.get("Max Drawdown", "0%")
            }
            yearly_stats.append(row)

        df_yearly = pd.DataFrame(yearly_stats)
        print(df_yearly.to_string(index=False))
        print("[*] Indicates strategy outperformed Buy & Hold in that specific metric\n")

# Visualization
def compare_equity(bt_dict):
    plt.figure(figsize=(14, 7))

    for name, bt in bt_dict.items():
        if name == "Buy & Hold":
            continue

        if name == "Strategy 3":
            plt.plot(
                bt["Date"],
                bt["Equity"],
                label=name,
                linewidth=2.5,
            )
        else:
            plt.plot(
                bt["Date"],
                bt["Equity"],
                label=name,
                linewidth=1.8,
            )

    plt.axvline(
        pd.to_datetime(OOS_START_DATE),
        color="black",
        linestyle="--",
        alpha=0.7,
        linewidth=1.5,
        label="Out-of-Sample Split",
    )

    plt.title("Equity Curves of the Proposed Strategies")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Portfolio Value")

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        root / "data" / "backtesting_plot.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


# Main Execution
def main():
    print("Loading signals and data...")
    prices, sig1, sig2, sig3 = load_data()

    if prices is None: return

    print(f"Running Backtest with a {POSITION_THRESHOLD*100}% trade threshold...")

    # 1. Run Standard Backtest (WITH COSTS)
    bt1 = run_backtest(prices, sig1)
    bt2 = run_backtest(prices, sig2)
    bt3 = run_backtest(prices, sig3)

    # 2. Run Frictionless Backtest (NO COSTS)
    bt1_nc = run_backtest(prices, sig1, comm=0.0, slip=0.0)
    bt2_nc = run_backtest(prices, sig2, comm=0.0, slip=0.0)
    bt3_nc = run_backtest(prices, sig3, comm=0.0, slip=0.0)

    buy_hold_signals = pd.DataFrame({"Date": prices["Date"], "Target_Position": 1.0})
    bt_bh = run_backtest(prices, buy_hold_signals, threshold=0.0, comm=0.0, slip=0.0)

    results_bt = {"Strategy 1": bt1, "Strategy 2": bt2, "Strategy 3": bt3, "Buy & Hold": bt_bh}
    results_bt_nc = {"Strategy 1": bt1_nc, "Strategy 2": bt2_nc, "Strategy 3": bt3_nc, "Buy & Hold": bt_bh}

    # Split into IS and OOS
    metrics_is, metrics_oos = [], []
    metrics_is_nc, metrics_oos_nc = [], []

    for name in results_bt.keys():
        # With Costs
        bt = results_bt[name]
        metrics_is.append(calculate_metrics(bt[bt['Date'] < OOS_START_DATE].copy(), label=name))
        metrics_oos.append(calculate_metrics(bt[bt['Date'] >= OOS_START_DATE].copy(), label=name))

        # No Costs
        bt_nc = results_bt_nc[name]
        metrics_is_nc.append(calculate_metrics(bt_nc[bt_nc['Date'] < OOS_START_DATE].copy(), label=name))
        metrics_oos_nc.append(calculate_metrics(bt_nc[bt_nc['Date'] >= OOS_START_DATE].copy(), label=name))

    print("\n" + "="*65)
    print(f"IN-SAMPLE METRICS (Pre-{OOS_START_DATE}) - WITH COSTS")
    print("="*65)
    print(pd.DataFrame(metrics_is).to_string(index=False))

    print("\n" + "="*65)
    print(f"IN-SAMPLE METRICS (Pre-{OOS_START_DATE}) - NO COSTS")
    print("="*65)
    print(pd.DataFrame(metrics_is_nc).to_string(index=False))

    print("\n" + "="*65)
    print(f"OUT-OF-SAMPLE METRICS ({OOS_START_DATE} Onwards) - WITH COSTS")
    print("="*65)
    print(pd.DataFrame(metrics_oos).to_string(index=False))

    print("\n" + "="*65)
    print(f"OUT-OF-SAMPLE METRICS ({OOS_START_DATE} Onwards) - NO COSTS")
    print("="*65)
    print(pd.DataFrame(metrics_oos_nc).to_string(index=False))

    # Calculate detailed yearly metrics based on WITH COSTS standard
    display_detailed_yearly_metrics(results_bt)

    print("\nPlotting Equity Curves (With Costs)...")
    compare_equity(results_bt)

if __name__ == "__main__":
    main()
