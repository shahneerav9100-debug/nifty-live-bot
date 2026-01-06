import yfinance as yf
import pandas_ta as ta
import requests
import time
import random
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION ---
TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"
SYMBOL = "BTC-USD"

# --- TRADE STATE ---
active_trade = None  # Stores details like {'type': 'BUY', 'entry': 25000, 'sl': 24950, 'target': 25100}
daily_signals = []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: pass

def get_ist_time():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

def run_bot():
    # TEST 1: Immediate Message
    send_telegram("Checking connection... If you see this, Step 1 is successful!")
    
    # TEST 2: Data Check
    try:
        df = yf.download("^NSEI", period="1d", interval="15m")
        price = round(df.iloc[-1]['Close'], 2)
        send_telegram(f"I can see the market! Last Nifty Close was: {price}")
    except Exception as e:
        send_telegram(f"I am having trouble seeing data. Error: {e}")

if __name__ == "__main__":

    run_bot()


