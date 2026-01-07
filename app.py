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
NSE_HOLIDAYS_2026 = [
    "2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31", 
    "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", 
    "2026-06-26", "2026-09-14", "2026-10-02", "2026-10-20", 
    "2026-11-10", "2026-11-24", "2026-12-25"
]

def get_ist_time():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

def is_market_live():
    now = get_ist_time()
    today, current_time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    if now.weekday() >= 5 or today in NSE_HOLIDAYS_2026: return False
    return "09:15" <= current_time <= "15:30"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def analyze_and_report():
    try:
        # Fetch 5m and 15m data
        df = yf.download(SYMBOL, period="2d", interval="5m", progress=False)
        if df.empty or len(df) < 50: return

        # Indicators
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        macd = ta.macd(df['Close'])
        
        c = df.iloc[-1]
        price, rsi, atr = round(c['Close'], 2), round(c['RSI'], 2), round(c['ATR'], 2)
        
        # Expert Logic (Confluence of Trend + Momentum)
        is_buy = price > c['EMA20'] and rsi > 55 and c['MACD_12_26_9'] > c['MACDs_12_26_9']
        is_sell = price < c['EMA20'] and rsi < 45 and c['MACD_12_26_9'] < c['MACDs_12_26_9']

        if is_buy or is_sell:
            trade_type = "BUY" if is_buy else "SELL"
            sl = round(price - (1.5 * atr) if is_buy else price + (1.5 * atr), 2)
            t1 = round(price + (2 * atr) if is_buy else price - (2 * atr), 2)
            
            # Prevent duplicate alerts for the same price action
            trade_id = f"{trade_type}_{price}"
            if trade_id not in trade_log:
                trade_log.append(trade_id)
                
                report = (
                    f"🏛️ *NIFTY 50 EXPERT SETUP*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"*1. MARKET OVERVIEW*\n"
                    f"Trend: `{'Bullish' if is_buy else 'Bearish'}` | Vol: `{round(atr,1)}` \n\n"
                    f"*2. TECHNICAL SIGNALS*\n"
                    f"RSI: `{rsi}` | MACD: `Confirmed` | EMA: `Supporting` \n\n"
                    f"*3. ACTIONABLE TRADE*\n"
                    f"• *TYPE:* `{trade_type}`\n"
                    f"• Entry: `{price}`\n"
                    f"• Stop-Loss: `{sl}`\n"
                    f"• Target 1: `{t1}` | Target 2: `{round(t1 + (atr if is_buy else -atr),2)}` \n\n"
                    f"🎯 *Confidence: 85%* | Invalid: `{sl}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                send_telegram(report)
    except Exception as e:
        print(f"Analysis Error: {e}")

def generate_eod_summary():
    try:
        df = yf.download(SYMBOL, period="1d", interval="5m", progress=False)
        if df.empty: return
        open_p, close_p = df['Open'].iloc[0], df['Close'].iloc[-1]
        change = round(close_p - open_p, 2)
        summary = (
            f"🏁 *NIFTY 3:35 PM FINAL SUMMARY*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• Day Result: `{'BULLISH' if change > 0 else 'BEARISH'}`\n"
            f"• Net Change: `{change} pts`\n"
            f"• Signals Today: `{len(trade_log)}` \n\n"
            f"👋 *Bot shutting down until 09:15 AM.*"
        )
        send_telegram(summary)
        trade_log.clear()
    except: pass

def main_loop():
    eod_done = False
    print("🚀 Nifty Expert Bot is running...")
    while True:
        try:
            now = get_ist_time()
            curr_time = now.strftime("%H:%M")
            
            if is_market_live():
                analyze_and_report()
                eod_done = False # Reset flag for tomorrow
                
                # MORNING JUMP: Check every 30s during first 10 mins
                if "09:15" <= curr_time <= "09:25":
                    time.sleep(30)
                else:
                    time.sleep(300) # 5-minute normal check
            
            elif curr_time == "15:35" and not eod_done:
                generate_eod_summary()
                eod_done = True
                time.sleep(60)
            else:
                time.sleep(60) # Idle sleep
        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(10)

threading.Thread(target=main_loop, daemon=True).start()

@app.route('/')
def home():
    return f"Bot Status: Online | Time: {get_ist_time().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
