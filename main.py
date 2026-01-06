import yfinance as yf
import pandas_ta as ta
import requests
import time
import random
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION ---
TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"
SYMBOL = "^NSEI"

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
    global active_trade, daily_signals
    send_telegram("🛰️ *Nifty Tracker Bot Online*")

    while True:
        now = get_ist_time()
        current_time = now.strftime("%H:%M")
        
        # 1. MARKET HOURS CHECK
        if "09:15" <= current_time <= "15:30" and now.weekday() < 5:
            try:
                # Fetch data (randomize agent to avoid block)
                df = yf.download(SYMBOL, period="2d", interval="15m", progress=False)
                last_price = round(df.iloc[-1]['Close'], 2)

                # A. MONITOR ACTIVE TRADE
                if active_trade:
                    trade_type = active_trade['type']
                    entry = active_trade['entry']
                    sl = active_trade['sl']
                    tg = active_trade['target']

                    if trade_type == "BUY":
                        if last_price >= tg:
                            send_telegram(f"💰 *TARGET HIT!* \nExit: {last_price} \nProfit: {round(last_price-entry, 2)} pts")
                            active_trade = None
                        elif last_price <= sl:
                            send_telegram(f"🛑 *STOP LOSS HIT!* \nExit: {last_price} \nLoss: {round(last_price-entry, 2)} pts")
                            active_trade = None
                    
                    elif trade_type == "SELL":
                        if last_price <= tg:
                            send_telegram(f"💰 *TARGET HIT!* \nExit: {last_price} \nProfit: {round(entry-last_price, 2)} pts")
                            active_trade = None
                        elif last_price >= sl:
                            send_telegram(f"🛑 *STOP LOSS HIT!* \nExit: {last_price} \nLoss: {round(entry-last_price, 2)} pts")
                            active_trade = None

                # B. SCAN FOR NEW ENTRY (Only if not in a trade)
                else:
                    df['EMA'] = ta.ema(df['Close'], length=20)
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
                    
                    row = df.iloc[-1]
                    rsi, vwap, ema = row['RSI'], row['VWAP'], row['EMA']

                    if last_price > vwap and last_price > ema and rsi > 55:
                        active_trade = {
                            'type': 'BUY', 'entry': last_price, 
                            'sl': round(last_price - 40, 2), 'target': round(last_price + 60, 2)
                        }
                        send_telegram(f"🚀 *BUY ENTRY*\nPrice: {last_price}\nSL: {active_trade['sl']}\nTgt: {active_trade['target']}")
                        daily_signals.append(active_trade)

                    elif last_price < vwap and last_price < ema and rsi < 45:
                        active_trade = {
                            'type': 'SELL', 'entry': last_price, 
                            'sl': round(last_price + 40, 2), 'target': round(last_price - 60, 2)
                        }
                        send_telegram(f"📉 *SELL ENTRY*\nPrice: {last_price}\nSL: {active_trade['sl']}\nTgt: {active_trade['target']}")
                        daily_signals.append(active_trade)

            except Exception as e: print(f"Error: {e}")
            
            time.sleep(random.randint(45, 60)) # Faster check when tracking a trade

        else:
            # Market Closed Logic (Reset daily summary etc.)
            time.sleep(600)

if __name__ == "__main__":
    run_bot()