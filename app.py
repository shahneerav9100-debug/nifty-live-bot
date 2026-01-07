import os, threading, requests, time, sys
from flask import Flask
from datetime import datetime, timezone, timedelta
import yfinance as yf
import pandas_ta as ta

# --- CONFIG ---
TOKEN = "8119396994:AAFdhHdq8mRwaFyGsfxnzn5vMTFo43Nnl_Q"
CHAT_ID = "8033862332"

SYMBOL = "^NSEI"

app = Flask(__name__)
trade_log = [] 

# Official NSE Equity Holidays 2026
NSE_HOLIDAYS_2026 = ["2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31", "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", "2026-06-26", "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-10", "2026-11-24", "2026-12-25"]

def get_ist_time():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def generate_eod_summary():
    global trade_log
    df = yf.download(SYMBOL, period="1d", interval="5m", progress=False)
    if df.empty: return
    
    close_p = df['Close'].iloc[-1]
    open_p = df['Open'].iloc[0]
    change = round(close_p - open_p, 2)
    
    summary = (
        f"🏁 *NIFTY 3:35 PM FINAL SHUTDOWN*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"• Final Price: `{round(close_p, 2)}`\n"
        f"• Day Result: `{'Bullish' if change > 0 else 'Bearish'}`\n"
        f"• Signals Sent: `{len(trade_log)}` \n\n"
        f"👋 *Bot is now SHUTTING DOWN until 09:15 AM tomorrow.*"
    )
    send_telegram(summary)
    trade_log = []

def analyze_and_report():
    # ... [Same technical analysis logic as previous version] ...
    pass

def main_loop():
    print("🤖 Bot Started. Waiting for 09:15 AM IST...")
    while True:
        now = get_ist_time()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        # 1. STOP CONDITION: Exactly 3:35 PM
        if current_time == "15:35":
            generate_eod_summary()
            print("🛑 Market Closed. Shutting down for the day.")
            # Wait until 9:14 AM next day to resume (approx 17.5 hours)
            time.sleep(63000) 
            continue

        # 2. RUN CONDITION: Market Hours
        if now.weekday() < 5 and today not in NSE_HOLIDAYS_2026 and "09:15" <= current_time <= "15:30":
            analyze_and_report()
            time.sleep(300) # Check every 5 mins
        else:
            time.sleep(60) # Idle check during off-hours

threading.Thread(target=main_loop, daemon=True).start()

@app.route('/')
def home():
    return f"Nifty Expert Bot Status: Active | IST: {get_ist_time().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

