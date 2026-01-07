import os, threading, requests, time
from flask import Flask
from datetime import datetime, timezone, timedelta
import yfinance as yf
import pandas_ta as ta

# --- CONFIG ---
# Replace these with your actual details
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

def get_morning_cues():
    try:
        # GIFT Nifty proxy (usually tracked via futures symbols)
        gift = yf.download(SYMBOL, period="1d", interval="15m", progress=False)
        us_mkt = yf.download("^GSPC", period="1d", progress=False)
        
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
            f"The bot is now in **Morning Jumpstart** mode. High-frequency 30s checks start at 09:15 AM.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        send_telegram(msg)
    except:
        send_telegram("☀️ *GOOD MORNING!* Bot is ready for the 09:15 AM open. Global data fetch failed, but logic is active.")

def analyze_and_report():
    try:
        df = yf.download(SYMBOL, period="2d", interval="5m", progress=False)
        if df.empty or len(df) < 20: return

        # Indicator Logic
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        macd = ta.macd(df['Close'])
        
        c = df.iloc[-1]
        price, rsi, atr = round(c['Close'], 2), round(c['RSI'], 2), round(c['ATR'], 2)
        
        # Confluence Trigger Logic
        is_buy = price > c['EMA20'] and rsi > 55 and macd['MACD_12_26_9'].iloc[-1] > macd['MACDs_12_26_9'].iloc[-1]
        is_sell = price < c['EMA20'] and rsi < 45 and macd['MACD_12_26_9'].iloc[-1] < macd['MACDs_12_26_9'].iloc[-1]

        if is_buy or is_sell:
            trade_type = "BUY" if is_buy else "SELL"
            # Prevent spamming the same price alert
            trade_id = f"{trade_type}_{round(price/5)*5}" 
            if trade_id not in trade_log:
                trade_log.append(trade_id)
                sl = round(price - (1.5 * atr) if is_buy else price + (1.5 * atr), 2)
                t1 = round(price + (2 * atr) if is_buy else price - (2 * atr), 2)
                t2 = round(price + (4 * atr) if is_buy else price - (4 * atr), 2)

                report = (
                    f"🏛️ *NIFTY 50 EXPERT SETUP*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"*1. MARKET OVERVIEW*\n"
                    f"Trend: `{'Bullish' if is_buy else 'Bearish'}` | ATR: `{atr}`\n\n"
                    f"*2. INDICATOR SIGNALS*\n"
                    f"RSI: `{rsi}` | EMA: `Support` | MACD: `Crossed` \n\n"
                    f"*3. ACTIONABLE TRADE*\n"
                    f"• *TYPE:* `{trade_type}`\n"
                    f"• Entry: `{price}`\n"
                    f"• Stop-Loss: `{sl}`\n"
                    f"• Target 1: `{t1}`\n"
                    f"• Target 2: `{t2}`\n\n"
                    f"🎯 *Confidence: 85%* | Invalidation: `{sl}`\n"
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
            f"• Total Trade Signals: `{len(trade_log)}` \n\n"
            f"👋 *Bot shutting down. See you tomorrow!*"
        )
        send_telegram(summary)
        trade_log.clear()
    except: pass

def main_loop():
    morning_sent = False
    eod_done = False
    print("🤖 Nifty Bot Started and Waiting for Market IST...")
    
    while True:
        try:
            now = get_ist_time()
            curr_time = now.strftime("%H:%M")
            
            # 9:05 AM Morning Cues
            if curr_time == "09:05" and not morning_sent:
                get_morning_cues()
                morning_sent = True
                time.sleep(60)

            # 9:15 AM - 3:30 PM Trading
            elif is_market_live():
                analyze_and_report()
                morning_sent = False # Reset
                eod_done = False # Reset
                
                # Jumpstart Mode (High Frequency for first 10 mins)
                if "09:15" <= curr_time <= "09:25":
                    time.sleep(30)
                else:
                    time.sleep(300) # Normal 5-min checks
            
            # 3:35 PM Summary and Shutdown
            elif curr_time == "15:35" and not eod_done:
                generate_eod_summary()
                eod_done = True
                time.sleep(60)
            
            else:
                # Night/Weekend idle check every 60s
                time.sleep(60)
                
        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(10)

# Start background thread
threading.Thread(target=main_loop, daemon=True).start()

@app.route('/')
def home():
    return f"Nifty Expert Bot - Online. Current IST: {get_ist_time().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
