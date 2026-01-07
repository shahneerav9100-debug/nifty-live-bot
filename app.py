import os, threading, requests, time, sys
from flask import Flask
from datetime import datetime, timezone, timedelta
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- CONFIG ---
TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
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
    except: pass

def get_morning_cues():
    try:
        # Request with multi_level_index=False for simpler structure
        gift = yf.download(SYMBOL, period="1d", interval="15m", progress=False, multi_level_index=False)
        us_mkt = yf.download("^GSPC", period="1d", progress=False, multi_level_index=False)
        
        change = round(gift['Close'].iloc[-1] - gift['Open'].iloc[0], 2)
        direction = "🟢 BULLISH GAP" if change > 0 else "🔴 BEARISH GAP"
        
        msg = (
            f"☀️ *GOOD MORNING! MARKET PREP*\n"
            f"📅 {get_ist_time().strftime('%d %b %Y')} | 09:05 AM\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 *GLOBAL CUES*\n"
            f"• Sentiment: `{direction}`\n"
            f"• Wall Street (S&P500): `{'✅ Green' if us_mkt['Close'].iloc[-1] > us_mkt['Open'].iloc[0] else '❌ Red'}`\n\n"
            f"🚀 *STRATEGY*\n"
            f"Bot is active. Checking every 30s during opening volatility.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        send_telegram(msg)
    except:
        send_telegram("☀️ *GOOD MORNING!* Bot is active for the 09:15 AM open.")

def analyze_and_report():
    try:
        # Use multi_level_index=False to avoid the "Object" dtype error
        df = yf.download(SYMBOL, period="2d", interval="5m", progress=False, multi_level_index=False)
        
        if df.empty or len(df) < 30: return

        # Ensure numeric conversion for all price columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Expert Indicator Logic
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        macd = ta.macd(df['Close'])
        
        c = df.iloc[-1]
        price = round(c['Close'], 2)
        rsi = round(c['RSI'], 2)
        atr = round(c['ATR'], 2)
        
        # Confluence Trigger
        is_buy = price > c['EMA20'] and rsi > 55 and macd['MACD_12_26_9'].iloc[-1] > macd['MACDs_12_26_9'].iloc[-1]
        is_sell = price < c['EMA20'] and rsi < 45 and macd['MACD_12_26_9'].iloc[-1] < macd['MACDs_12_26_9'].iloc[-1]

        if is_buy or is_sell:
            trade_type = "BUY" if is_buy else "SELL"
            trade_id = f"{trade_type}_{round(price/10)*10}" 
            
            if trade_id not in trade_log:
                trade_log.append(trade_id)
                sl = round(price - (1.5 * atr) if is_buy else price + (1.5 * atr), 2)
                t1 = round(price + (2.5 * atr) if is_buy else price - (2.5 * atr), 2)

                report = (
                    f"🏛️ *NIFTY 50 EXPERT SETUP*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"Action: *{trade_type}* @ `{price}`\n"
                    f"Stop-Loss: `{sl}`\n"
                    f"Target: `{t1}`\n"
                    f"RSI: `{rsi}` | Vol: `{round(atr,1)}` \n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                send_telegram(report)
    except Exception as e:
        print(f"Analysis Error: {e}")

def generate_eod_summary():
    try:
        df = yf.download(SYMBOL, period="1d", interval="5m", progress=False, multi_level_index=False)
        if df.empty: return
        change = round(df['Close'].iloc[-1] - df['Open'].iloc[0], 2)
        summary = (
            f"🏁 *NIFTY FINAL SUMMARY*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• Change: `{change} pts`\n"
            f"• Signals Today: `{len(trade_log)}` \n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        send_telegram(summary)
        trade_log.clear()
    except: pass

def main_loop():
    morning_sent, eod_done = False, False
    while True:
        try:
            now = get_ist_time()
            curr_time = now.strftime("%H:%M")
            
            if curr_time == "09:05" and not morning_sent:
                get_morning_cues(); morning_sent = True; time.sleep(60)
            elif is_market_live():
                analyze_and_report()
                morning_sent, eod_done = False, False
                time.sleep(30 if "09:15" <= curr_time <= "09:25" else 300)
            elif curr_time == "15:35" and not eod_done:
                generate_eod_summary(); eod_done = True; time.sleep(60)
            else:
                time.sleep(60)
        except Exception as e:
            print(f"Loop Error: {e}"); time.sleep(10)

threading.Thread(target=main_loop, daemon=True).start()

@app.route('/')
def home():
    return f"Bot Active. Time: {get_ist_time().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
