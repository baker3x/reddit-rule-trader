from core.screener import screen_stocks
from core.notifier import send_trade_alert
from datetime import datetime
import logging
import os

# Setup logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, 
f"run_{datetime.today().strftime('%Y-%m-%d')}.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
format='%(asctime)s - %(message)s')

# Full ticker universe to scan (replace with your list or source)
TICKERS = [
    "AAPL", "TSLA", "AMD", "NVDA", "MSFT",
    "META", "NFLX", "BABA", "PLTR", "SNAP"
]

if __name__ == "__main__":
    try:
        logging.info("Starting daily screen...")
        picks = screen_stocks(TICKERS)
        logging.info(f"Selected tickers: {picks}")

        if picks:
            send_trade_alert(picks, hold_days=3)
            logging.info("Trade alert sent successfully.")
        else:
            logging.info("No tickers met the criteria today.")

    except Exception as e:
        logging.error(f"Error occurred: {e}")

