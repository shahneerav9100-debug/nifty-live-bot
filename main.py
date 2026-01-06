import requests
import time

TOKEN = "8598972684:AAFAjrhlbY9Uyz7cYMcxJM0kl1lMVkTT0kQ"
CHAT_ID = "8033862332"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram Response: {r.status_code} - {r.text}", flush=True)
    except Exception as e:
        print(f"Telegram Failed: {e}", flush=True)

def run_bot():
    print("RUN_BOT FUNCTION STARTED", flush=True)
    # This message should come to your phone immediately
    send_telegram("✅ CONNECTION TEST: I am running on Render!")
    
    while True:
        print("Bot is heartbeating...", flush=True)
        time.sleep(60)


