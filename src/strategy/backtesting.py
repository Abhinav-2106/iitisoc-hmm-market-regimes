import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

root = Path(__file__).resolve().parents[2]
clean_data = root / "data"

TRADING_DAYS = 252
commission = 0.0005  #broker commission
slippagefactor = 0.05 #slippage factor for daily volatility


#data loading
def load_data():
    prices = pd.read_csv(clean_data / "clean_data.csv")#loading the clean_data.csv
    prices["Date"] = pd.to_datetime(prices["Date"])

    #load Lord Shubham's precomputed signal files
    try:
        sig1 = pd.read_csv(clean_data / "signals_strategy_1.csv")
        sig2 = pd.read_csv(clean_data / "signals_strategy_2.csv")
        sig1["Date"] = pd.to_datetime(sig1["Date"])
        sig2["Date"] = pd.to_datetime(sig2["Date"])
    except FileNotFoundError as e:
        print(f"couldnt load csv file from {e}")
        return None, None, None

    return prices, sig1, sig2


#backtest engine
def run_backtest(prices, signals):
    #fusing prices of nifty50 with signals
    bt = prices.merge(signals, on="Date", how="inner")

    # Ensure columns match expected naming conventions
    if "Target_Position" not in bt.columns:
        # Fallback in case Shubham named the output column "signal" or "position"
        signal_col = [col for col in bt.columns if col.lower() in ["signal", "position"]][0]
        bt["Target_Position"] = bt[signal_col]

    bt["Return"] = bt["Close"].pct_change()#changes in nifty50 prices day by day

    # preventing look ahead bias
    bt["Position"] = bt["Target_Position"].shift(1).fillna(0)

    # transaction cost
    bt["Position_Change"] = bt["Position"].diff().abs().fillna(bt["Position"].abs())#calculating turnover
    dslippage = bt["Return"].abs() * slippagefactor#dynamic slippage
    bt["Cost"] = bt["Position_Change"] * (commission + dslippage)#total

    bt["Strategy_Return"] = (bt["Position"] * bt["Return"]) - bt["Cost"]
    bt["Strategy_Return"] = bt["Strategy_Return"].fillna(0)

    bt["Equity"] = (1 + bt["Strategy_Return"]).cumprod()
    bt["Market_Equity"] = (1 + bt["Return"].fillna(0)).cumprod()

    return bt


#metrics
def calculate_metrics(bt, label="Strategy"):
  #cagr
    years = (bt["Date"].iloc[-1] - bt["Date"].iloc[0]).days / 365.25
    cagr = (bt["Equity"].iloc[-1] ** (1 / years)) - 1 if years > 0 else 0

    #sharpe
    std = bt["Strategy_Return"].std()
    sharpe = (bt["Strategy_Return"].mean() / std) * np.sqrt(TRADING_DAYS) if std > 0 else 0

    #sortino
    downside = bt["Strategy_Return"][bt["Strategy_Return"] < 0]
    sortino = (bt["Strategy_Return"].mean() / downside.std()) * np.sqrt(TRADING_DAYS) if not downside.empty else 0

    #maximum drawdown
    drawdown = (bt["Equity"] / bt["Equity"].cummax()) - 1
    max_dd = drawdown.min()

    #calmar
    calmar = cagr / abs(max_dd) if max_dd < 0 else 0

    #winrate
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

#visualizayion
def compare_equity(bt_dict):
    plt.figure(figsize=(12, 6))
    for name, bt in bt_dict.items():
        plt.plot(bt["Date"], bt["Equity"], label=name)
    plt.title("Strategies vs Benchmark")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

#main execution
def main():
    print("Loading signals and data")
    prices, sig1, sig2 = load_data()

    if prices is None:
        return

    print("Running Backtest")

    #strategy 1
    bt1 = run_backtest(prices, sig1)

    #strategy 2
    bt2 = run_backtest(prices, sig2)

    #buy & hold
    buy_hold_signals = pd.DataFrame({"Date": prices["Date"], "Target_Position": 1.0})
    bt_bh = run_backtest(prices, buy_hold_signals)

    results_bt = {
        "Strategy 1": bt1,
        "Strategy 2": bt2,
        "Buy & Hold": bt_bh
    }

    metrics_list = [
        calculate_metrics(bt1, label="Strategy 1"),
        calculate_metrics(bt2, label="Strategy 2"),
        calculate_metrics(bt_bh, label="Buy & Hold")
    ]


    print("PERFORMANCE METRICS")
    metrics_df = pd.DataFrame(metrics_list)
    print(metrics_df.to_string(index=False))

    print("\nPlotting Equity Curves...")
    compare_equity(results_bt)

if __name__ == "__main__":
    main()