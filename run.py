from subprocess import run
import sys

steps= [
    ("Train HMM and feature engineering", ["python", "src/hmm/base_hmm.py"]),
    ("Generating forcast datasets", ["python", "src/strategy/transition_forecast.py"]),
    ("Running Strategy 1", ["python", "src/strategy/strategy_engine_1.py"]),
    ("Running Strategy 2", ["python", "src/strategy/strategy_engine_2.py"]),
    ("Running Strategy 3", ["python", "src/strategy/strategy_engine_3.py"]),
    ("Backtesting", ["python", "src/strategy/backtesting.py"])
]

for name, command in steps:
    print(name)

    result = run(command)

    if result.returncode != 0:
        print(f"{name} failed.")

        sys.exit(result.returncode)

