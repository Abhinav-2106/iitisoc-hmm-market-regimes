
# Market Regime Interpretation (6-State HMM)

| State   | Interpretation     | Category                |
| ------- | ------------------ | ----------------------- |
| State 0 | Normal Bull        | Bullish                 |
| State 1 | Correction         | Bearish                 |
| State 2 | Neutral / Recovery | Sideways / Transitional |
| State 3 | Crisis / Panic     | Bearish                 |
| State 4 | Aggressive Bull    | Bullish                 |
| State 5 | Calm Bull          | Bullish                 |

## Regime Characteristics

### State 4 — Aggressive Bull

* Strong positive returns
* High market participation
* Strong trend persistence
* Higher volatility than normal bull markets

### State 0 — Normal Bull

* Stable positive returns
* Healthy upward trend
* Moderate volatility

### State 5 — Calm Bull

* Positive returns
* Low volatility
* Stable market conditions

### State 2 — Neutral / Recovery

* Market consolidation
* Trend uncertainty
* Transition between bull and bear phases
* Suitable for mean reversion strategies

### State 1 — Correction

* Temporary market decline
* Elevated volatility
* Increased downside risk

### State 3 — Crisis / Panic

* Severe market stress
* Extremely high volatility
* Large drawdowns
* Capital preservation becomes the primary objective



# Strategy 1: Regime-Based Asset Allocation

| State   | Regime             | Allocation |
| ------- | ------------------ | ---------- |
| State 4 | Aggressive Bull    | 100%       |
| State 0 | Normal Bull        | 100%       |
| State 5 | Calm Bull          | 100%       |
| State 2 | Neutral / Recovery | 50%        |
| State 1 | Correction         | 0%         |
| State 3 | Crisis / Panic     | 0%         |

## Rationale

Bullish states:

* Maximize exposure to capture upward trends.

Neutral / Recovery:

* Partial allocation due to uncertainty.

Correction and Crisis:

* Move to cash to reduce drawdowns and preserve capital.


# Strategy 2: Regime-Adaptive Trading

| State   | Regime             | Strategy                     |
| ------- | ------------------ | ---------------------------- |
| State 4 | Aggressive Bull    | Momentum Trading             |
| State 0 | Normal Bull        | Trend Following              |
| State 5 | Calm Bull          | Buy & Hold / Trend Following |
| State 2 | Neutral / Recovery | Mean Reversion               |
| State 1 | Correction         | Cash / Defensive Position    |
| State 3 | Crisis / Panic     | Cash / Risk-Off Mode         |

## Strategy Selection Logic

### Aggressive Bull

* Momentum indicators
* Breakout strategies
* Maximum market exposure

### Normal Bull

* Trend-following systems
* Moving-average filters

### Calm Bull

* Long-only exposure
* Reduced trading frequency

### Neutral / Recovery

* RSI-based mean reversion
* Bollinger Band reversion strategies

### Correction

* Exit positions
* Preserve capital

### Crisis / Panic

* No new long positions
* Remain in cash
* Focus on drawdown protection



# Structure
strategy/

├── transition_forecast.py
├── strategy_engine.py
├── position_sizer.py

├── strategies/
│   ├── aggressive_bull.py
│   ├── normal_bull.py
│   ├── calm_bull.py
│   ├── neutral.py
│   ├── correction.py
│   └── crisis.py

└── backtest.py
