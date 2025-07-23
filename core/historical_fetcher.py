import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
from dotenv import load_dotenv

load_dotenv()

TRADIER_TOKEN = os.getenv("TRADIER_API_KEY")
TRADIER_URL = "https://api.tradier.com/v1/markets/history"
HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}

DATA_DIR = "data/historical"
os.makedirs(DATA_DIR, exist_ok=True)

START_YEAR = 2003
CHUNK_YEARS = 1  # Tradier may not allow 20+ year ranges in one call


def fetch_and_save(ticker: str):
    filepath = os.path.join(DATA_DIR, f"{ticker}.parquet")
    if os.path.exists(filepath):
        print(f"{ticker} already exists. Skipping.")
        return

    print(f"Fetching {ticker}...")
    all_data = []
    for year in range(START_YEAR, datetime.now().year + 1, CHUNK_YEARS):
        start = datetime(year, 1, 1).strftime("%Y-%m-%d")
        end = datetime(year + CHUNK_YEARS - 1, 12, 
31).strftime("%Y-%m-%d")
        params = {"symbol": ticker, "start": start, "end": end, 
"interval": "daily"}
        response = requests.get(TRADIER_URL, headers=HEADERS, 
params=params)
        if response.status_code != 200:
            print(f"Failed: {ticker} ({start} to {end}) => 
{response.text}")
            continue

        data = response.json().get("history", {}).get("day", [])
        all_data.extend(data)
        sleep(0.5)  # Be kind to the API

    if all_data:
        df = pd.DataFrame(all_data)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df = df.astype(float)
        df.to_parquet(filepath)
        print(f"Saved {ticker} ({len(df)} rows)")
    else:
        print(f"No data for {ticker}")


if __name__ == "__main__":
    TICKERS = [
        "AAPL", "TSLA", "AMD", "NVDA", "MSFT",
        "META", "NFLX", "BABA", "PLTR", "SNAP"
    ]

    for ticker in TICKERS:
        fetch_and_save(ticker)

