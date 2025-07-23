import pandas as pd
import numpy as np
import os
from typing import List
from core.screener import sma, atr

# Directory containing .parquet files (e.g., 2003+ data)
DATA_DIR = "data/historical"
HOLD_DAYS = 3


def load_data(ticker: str) -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, f"{ticker}.parquet")
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_parquet(filepath)
    df["SMA20"] = sma(df["close"], 20)
    df["ATR10"] = atr(df, 10)
    return df


def simulate_backtest(ticker: str) -> List[float]:
    df = load_data(ticker)
    if df.empty or len(df) < 60:
        return []

    returns = []
    for i in range(30, len(df) - HOLD_DAYS):
        today = df.iloc[i]

        if (
            today["close"] > today["SMA20"] and
            today["volume"] > 1_000_000 and
            today["ATR10"] > 0.05 * today["close"] and
            1 <= today["close"] <= 50
        ):
            entry_price = df.iloc[i + 1]["open"] if i + 1 < len(df) else 
today["close"]
            exit_idx = i + HOLD_DAYS
            if exit_idx < len(df):
                exit_price = df.iloc[exit_idx]["open"]
                gain = (exit_price - entry_price) / entry_price
                returns.append(gain)

    return returns


def evaluate_strategy(tickers: List[str]):
    all_returns = []
    for t in tickers:
        r = simulate_backtest(t)
        all_returns.extend(r)

    if not all_returns:
        print("No trades triggered.")
        return

    log_returns = np.log(np.array(all_returns) + 1)
    geom_mean = np.exp(np.mean(log_returns)) - 1
    print(f"Total trades: {len(all_returns)}")
    print(f"Geometric Mean Return: {geom_mean:.4f}")

    cumulative_log = np.cumsum(log_returns)
    pd.Series(cumulative_log).plot(title="Cumulative Log Return")


if __name__ == "__main__":
    TICKERS = [f.replace(".parquet", "") for f in os.listdir(DATA_DIR) if 
f.endswith(".parquet")]
    evaluate_strategy(TICKERS)

