# Market Regime Detection and Adaptive Trading using Hidden Markov Models

---

## Problem Statement

The selected period covers multiple economic cycles including prolonged bull markets, corrections, the COVID-19 market crash, post-pandemic recovery, and inflation-driven volatility. Since Hidden Markov Models learn hidden market regimes from historical transitions, exposing the model to diverse market conditions improves the robustness of the learned state transitions.

---

## Data Collection and Preproscessing   

**Status** : Completed

### Dataset Selection

We are using NIFTy 50 (^NSEI) as the primary dataset for the HMM training. 

Reasons for selection :

* Represents Indian equity market* COVID crash.
* High Inflation.

### Data Cleaning

The raw market data obtained from `yfinance` is first cleaned and organized to ensure it is ready for analysis. The hierarchical column structure is flattened into standard column names, the `Date` index is converted into a regular column, and unnecessary metadata is removed. The dataset is then sorted chronologically to preserve the correct order of observations before being saved as `clean_data.csv`, which serves as the input for the feature engineering and HMM training stages.
* Long historical data available for analysis.
* Widely used benchmark for Indian Quantitative Trading.

### Time Period

We are using 2010-2025.

Because it includes :

* Multiple occurance of all regimes.
* COVID crash.
* High Inflation.

### Data Cleaning

The raw market data downloaded using `yfinance` is cleaned and organized before analysis. The column names are standardized, the Date index is converted into a regular column, unnecessary metadata is removed, and the data is sorted chronologically. The cleaned dataset is then saved as `clean_data.csv` and used for feature engineering and HMM training.

---

## Feature Engineering

**Status** : Under Development (implemented 3 features may increase as per the requirements in the experminets).

Feature engineering is the process of converting raw market prices into meaningful statistical features that can be used by the Hidden Markov Model. Instead of training the HMM directly on prices, we train it on features that describe different aspects of market behaviour.

### Log Returns

We use **log returns** instead of raw price data for training the HMM because they provide a statistically normalized representation of price changes.

Using raw prices is not ideal because the same absolute price movement can have completely different meanings at different price levels. For example, a ₹10 increase from ₹100 to ₹110 represents a **10%** gain, whereas a ₹10 increase from ₹1000 to ₹1010 represents only a **1%** gain. Returns normalize these changes and make them comparable across different price levels.

We use **log returns** instead of simple returns because they are **additive over time**, making them more suitable for time-series modelling. They are also closer to being stationary, which is an important property for statistical models like the Hidden Markov Model.

### Rolling Volatility (20 Days)

Volatility is calculated as the rolling standard deviation of the log returns over a **20-day rolling window**.

This is one of the most important features because market regimes differ not only in the direction of price movement but also in the level of market uncertainty. For example, bullish markets generally exhibit relatively low volatility, whereas bear markets and financial crises are often characterized by sharp increases in volatility.

A **20-day window** is used because it approximately represents one trading month. This provides a good balance between responsiveness and stability. A much smaller window would react to every short-term fluctuation, making the volatility estimate noisy, while a much larger window would react too slowly to changes in market conditions.

### Daily Trading Range

The daily trading range is calculated as:

`(High - Low) / Close`

This feature measures the magnitude of intraday price movement relative to the closing price.

While rolling volatility captures price behaviour across multiple trading sessions, the daily trading range measures how active the market is within a single trading day. Larger trading ranges usually indicate increased market activity, higher uncertainty, or stronger buying and selling pressure.

The engineered features are finally stored in **`features.csv`**, which is used as the observation sequence for training the Hidden Markov Model.

---

## Hidden Markov Model Implementation

---

## Strategy Development

**Status:** Evolving *(Basic strategy implementation and backtesting have been completed. The regime-specific strategy is currently under development.)*

The objective of the trading strategy module is to convert the output of the Hidden Markov Model into actionable trading decisions. Throughout the development of this project, multiple versions of the strategy were implemented to improve the way regime information is utilized.

Rather than directly committing to a single approach, each version was designed to overcome the limitations of the previous one.

### Version 1 — Probability-Based Allocation

The first strategy uses the **current regime probabilities** generated by the Hidden Markov Model.

Each hidden state is assigned a **state weight**, representing the percentage of capital that should be allocated if the model is completely confident that the market is in that regime.

For example:

* **Bull State** → 100% allocation
* **Sideways State** → 50% allocation
* **Bear State** → 0% allocation

Since the HMM outputs probabilities rather than a single hard classification, the final portfolio allocation is calculated as the weighted average (dot product) of the state probability vector and the corresponding state weights.

This strategy naturally adjusts the portfolio allocation according to the confidence of the HMM.

---

### Version 2 — Transition Matrix Forecasting

The second version extends the previous strategy by introducing **one-step regime forecasting**.

Instead of making decisions solely based on today's detected regime, the transition matrix learned by the Hidden Markov Model is used to estimate the probability distribution of the market for the next trading day.

The forecasting process is implemented in **`transition_forecast.py`**.

If the current regime probability vector is

```text
v(t) = [Bull, Bear, Sideways]
```

then the forecasted probability vector is obtained using

```text
v(t+1) = v(t) × T
```

where **T** is the transition matrix learned during HMM training.

The motivation behind this approach was to make the trading strategy proactive rather than purely reactive.

However, during experimentation, it was observed that the forecasted probabilities were very similar to the current probabilities for most trading days. This is mainly because market regimes tend to be highly persistent, resulting in only marginal differences between the two strategies.

Although the improvement in backtesting performance was limited, this experiment validated the behaviour of the Hidden Markov Model and demonstrated that increasing model complexity does not necessarily lead to significantly better trading performance.

---

### Version 3 — Regime-Specific Trading Strategy

The current version under development focuses on **regime-specific trading logic**.

Instead of applying the same allocation rule under every market condition, the strategy first identifies the prevailing market regime and activates a trading strategy specifically designed for that regime.

The proposed mapping is:

* **Bull Market** → Momentum Strategy
* **Sideways Market** → Mean Reversion Strategy
* **Bear Market** → Cash / Capital Preservation

After selecting the appropriate trading strategy, the regime probabilities are used to determine the final position size.

In this approach:

* The **detected regime** determines **which trading strategy** should be executed.
* The **regime probabilities** determine **how aggressively** capital should be allocated.

This version aims to combine the strengths of statistical regime detection with traditional quantitative trading strategies, producing a more adaptive trading framework than the previous allocation-based approaches.

---
## Visualization and Analytics