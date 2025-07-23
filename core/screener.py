import requests
import pandas as pd
import datetime as dt
import os
from typing import List

TRADIER_TOKEN = os.getenv("TRADIER_API_KEY")
TRADIER_URL = "https://api.tradier.com/v1/markets/history"
HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}

UNIVERSE = [  # Example tickers (can be replaced with full universe)
    "AAPL", "TSLA", "AMD", "NVDA", "MSFT", "META", "NFLX", "BABA", "PLTR", 
"SNAP"
]

# --- Utility Functions ---
def fetch_eod(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Fetch daily historical data from Tradier"""
    params = {"symbol": ticker, "start": start, "end": end, "interval": 
"daily"}
    response = requests.get(TRADIER_URL, headers=HEADERS, params=params)
    data = response.json().get("history", {}).get("day", [])
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df = df.astype(float)
    return df

def atr(df: pd.DataFrame, period: int = 10) -> pd.Series:
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def sma(series: pd.Series, period: int = 20) -> pd.Series:
    return series.rolling(period).mean()

# --- Main Screener Logic ---
def screen_stocks(tickers: List[str]) -> List[str]:
    end_date = dt.datetime.today().strftime("%Y-%m-%d")
    start_date = (dt.datetime.today() - 
dt.timedelta(days=40)).strftime("%Y-%m-%d")

    picks = []
    for ticker in tickers:
        df = fetch_eod(ticker, start_date, end_date)
        if df.empty or len(df) < 20:
            continue

        df["SMA20"] = sma(df["close"], 20)
        df["ATR10"] = atr(df, 10)

        latest = df.iloc[-1]

        if (
            latest["close"] > latest["SMA20"] and
            latest["volume"] > 1_000_000 and
            latest["ATR10"] > 0.05 * latest["close"] and
            1 <= latest["close"] <= 50
        ):
            picks.append(ticker)

    return picks

if __name__ == "__main__":
    selected = screen_stocks(UNIVERSE)
    print("Today's picks:", selected)


